import os
from krules_core.base_functions import *
from krules_core.event_types import *
from krules_core.models import Rule
from krules_core.providers import subject_factory
import re

from jsonschema import validate


EXPECTED_PAYLOAD_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "group": {"type": "string"},
        "property_name": {"type": "string"},
        "value": {"type": ["string", "object", "number", "integer", "array", "boolean", "null"]},
    },
    "required": ["id", "group", "property_name", "value"],
}

TOPIC_RE = re.compile(
            "//pubsub.googleapis.com/projects/(?P<project>.*)/topics/ingestion-(?P<id>[0-9])+-?(?P<extra>.*)"
        )


class GetSubscription(FilterFunction):

    def execute(self, payload_dest) -> bool:
        match = TOPIC_RE.match(self.subject.event_info()["source"])
        if match is None:
            return False
        self.payload[payload_dest] = match.groupdict()
        return True


rulesdata: List[Rule] = [

    Rule(
        name="ingestion-first-receiver",
        subscribe_to=[EventType("google.cloud.pubsub.topic.v1.messagePublished")],
        description=
        """
            Pub/Sub message receiver from ingestion channels
        """,
        filters=[
            GetSubscription(payload_dest="subscription"),
            Filter(lambda payload: validate(payload, schema=EXPECTED_PAYLOAD_SCHEMA) or True)
        ],
        processing=[
            SetPayloadProperty(
                "subject",
                lambda payload: subject_factory(f"{payload['subscription']['id']}:{payload['group']}:{payload['id']}")
            ),
            SetSubjectExtendedProperty(
                "subscription",
                lambda payload: str(payload["subscription"]),
                subject=lambda payload: payload["subject"]
            ),
            SetSubjectExtendedProperty(
                "group",
                lambda payload: payload["group"],
                subject=lambda payload: payload["subject"]
            ),
            SetSubjectProperty(
                lambda payload: payload["property_name"],
                lambda payload: payload["value"],
                subject=lambda payload: payload["subject"]
            ),
        ]
    ),
]
