from krules_core.base_functions import *
from krules_core.models import Rule
from krules_core.event_types import SubjectPropertyChanged
from firestore import WriteDocument, WriteGroupColumns
from common.event_types import ENTITY_STATE_CHANGED, SUBJECT_PROPERTIES_DATA
from krules_core.providers import subject_factory
from datetime import datetime


class UpdateGroupColumns(ProcessingFunction):

    def execute(self, subscription, group, current_state):
        subject = subject_factory(f'schema|{subscription}|{group}')
        subject.set("columns", lambda v: sorted(list(set((v or []) + list(current_state.keys())))))


rulesdata: List[Rule] = [

    Rule(
        name="ingestion-first-receiver",
        subscribe_to=[SUBJECT_PROPERTIES_DATA],
        description=
        """
            Pub/Sub message receiver from ingestion channels
        """,
        filters=[
            SubjectNameMatch("^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$", payload_dest="entity_base_info"),
            Filter(lambda payload: "data" in payload and isinstance(payload["data"], dict) and len(payload["data"]))
        ],
        processing=[
            WriteDocument(
                collection=lambda payload:
                    f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}",
                document=lambda payload: payload['entity_base_info']['id'],
                data=lambda payload: payload["data"],
                subject_dest="current_state"
            ),
            SetSubjectProperties(
                props=lambda payload: payload["data"],
                unmuted="*"
            ),
        ]
    ),
    Rule(
        name="property-changed-propagation",
        subscribe_to=[SubjectPropertyChanged],
        description=
        """
        Propagate subject property changed event
        """,
        filters=[
            SubjectNameMatch(
                "^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$",
                payload_dest="entity_base_info"
            ),
            OnSubjectPropertyChanged("current_state")
        ],
        processing=[
            UpdateGroupColumns(
                subscription=lambda payload: payload["entity_base_info"]["subscription"],
                group=lambda payload: payload["entity_base_info"]["group"],
                current_state=lambda payload: payload["value"],
            ),
            Route(
                event_type=ENTITY_STATE_CHANGED,
                payload=lambda payload: {
                    "id": payload["entity_base_info"]["id"],
                    "subscription": payload["entity_base_info"]["subscription"],
                    "group": payload["entity_base_info"]["group"],
                    "state": payload["value"],
                    "prev_state": payload["old_value"],
                },
                dispatch_policy=DispatchPolicyConst.DIRECT
            )
        ]
    ),
    Rule(
        name="update-group-columns",
        subscribe_to=[SubjectPropertyChanged],
        description=
        """
        On property changed update group columns
        """,
        filters=[
            SubjectNameMatch(
                "^schema[|](?P<subscription>.+)[|](?P<group>.+)$",
                payload_dest="entity_base_info"
            ),
            OnSubjectPropertyChanged("columns")
        ],
        processing=[
            WriteGroupColumns(
                subscription=lambda payload: payload['entity_base_info']['subscription'],
                group=lambda payload: payload['entity_base_info']['group'],
                columns=lambda payload: payload["value"],
            )
        ]
    ),
    Rule(
        name="on-property-changed-update-event-sourcing",
        subscribe_to=[SubjectPropertyChanged],
        description=
        """
        Store state changes
        """,
        filters=[
            SubjectNameMatch(
                "^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$",
                payload_dest="entity_base_info"
            ),
            OnSubjectPropertyChanged("current_state")
        ],
        processing=[
            WriteDocument(
                collection=lambda payload:
                    f"event_sourcing",
                    # f"{payload['entity_base_info']['subscription']}/event_sourcing/{payload['entity_base_info']['group']}",
                data=lambda self: {
                    "datetime": datetime.now().isoformat(),
                    "subscription": self.payload['entity_base_info']['subscription'],
                    "group": self.payload['entity_base_info']['group'],
                    "id": self.payload['entity_base_info']['id'],
                    "state": self.subject.get("current_state"),
                    "changed_properties": [
                        k for k, v in self.payload["value"].items() if k not in self.payload[
                            "old_value"] or self.payload["old_value"].get(k) != v
                    ],
                    "origin_id": self.subject.event_info()["originid"]
                }
            ),
        ]
    ),
]
