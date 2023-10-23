import inspect
import json
import re
import os
import uuid
from datetime import datetime, timezone

import google.auth
import pydantic
from cloudevents.pydantic import CloudEvent
from google.cloud import pubsub_v1
from pydantic import ValidationError

_, project = google.auth.default()

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")
docs_path = f"projects/{project}/databases/{os.environ.get('FIRESTORE_DATABASE', '(default)')}/documents/"

pubsub_client = pubsub_v1.PublisherClient()


def get_value(obj):
    value = list(obj.values())[0]
    if "array_value" in obj:
        value = []
        for el in obj["array_value"]["values"]:
            value.append(get_value(el))
    elif "map_value" in obj:
        value = map_value_to_plain_dict(obj["map_value"])
    elif "null_value" in obj:
        return None
    return value


def map_value_to_plain_dict(obj):
    plain_dict = {}
    for k, v in obj["fields"].items():
        plain_dict[k] = get_value(v)
    return plain_dict


def json_decode(obj, properties):
    for prop in properties:
        if prop in obj:
            obj[prop] = json.loads(obj[prop])


def route(topic, event_type, subject, payload):

    class _JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if inspect.isfunction(obj):
                return obj.__name__
            elif isinstance(obj, object):
                return str(type(obj))
            return json.JSONEncoder.default(self, obj)

    if topic.startswith("projects/"):
        topic_path = topic
    else:
        topic_path = pubsub_client.topic_path(project, topic)
    event = CloudEvent(
        id=str(uuid.uuid4()),
        type=event_type,
        source="state-changes-dispatcher",
        subject=str(subject),
        data=payload,
        time=datetime.now(timezone.utc),
        datacontenttype="application/json",
        dataschema=""
    )
    event_obj = event.dict(exclude_unset=True)
    event_obj["data"] = json.dumps(event_obj["data"], cls=_JSONEncoder).encode()
    event_obj["time"] = event_obj["time"].isoformat()
    future = pubsub_client.publish(topic_path, **event_obj, contentType="text/json")
    future.add_done_callback(lambda _future: _future.result(timeout=60))


def index(data, context):
    """ Triggered by a change to a Firestore document.
    Args:
        data (dict): The event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """

    collection = context.resource.replace(docs_path, "")
    match = collection_regex.match(collection)
    collection_info = match.groupdict()
    update_mask = data.get("updateMask", {}).get("fieldPaths", [])
    if "_last_update" in update_mask:
        update_mask.remove("_last_update")
    handle_group(
        subscription=collection_info["subscription"],
        group=collection_info["group"],
        entity_id=collection_info["entity_id"],
        value=map_value_to_plain_dict(data["value"]),
        old_value=map_value_to_plain_dict(data["oldValue"]),
        update_mask=update_mask,
    )


def handle_group(subscription, group, entity_id, value, old_value, update_mask):

    if subscription == "0" and group == "wallbox.chargers":
        json_decode(value, ["ocpp_received", "ocpp_sent"])
        json_decode(old_value, ["ocpp_received", "ocpp_sent"])
        route(
            topic=os.environ["URMET_WALLBOX_TOPIC"],
            event_type="entity-state-changed",
            subject=f"entity|{subscription}|{group}|{entity_id}",
            payload={
                "entity_id": entity_id,
                "group": group,
                "subscription": int(subscription),
                "value": value,
                "old_value": old_value,
                "update_mask": update_mask
            }
        )
    elif subscription == "2" and group == "coldchain.items":
        if "temp" in update_mask:
            route(
                topic=os.environ["COLDCHAIN_ITEMS_TOPIC"],
                event_type="entity-state-changed",
                subject=f"entity|{subscription}|{group}|{entity_id}",
                payload={
                    "entity_id": entity_id,
                    "group": group,
                    "subscription": int(subscription),
                    "value": value,
                    "old_value": old_value,
                    "update_mask": update_mask
                }
            )
    elif subscription == "2" and group == "coldchain.locations":
        route(
            topic=os.environ["COLDCHAIN_LOCATIONS_TOPIC"],
            event_type="entity-state-changed",
            subject=f"entity|{subscription}|{group}|{entity_id}",
            payload={
                "entity_id": entity_id,
                "group": group,
                "subscription": int(subscription),
                "value": value,
                "old_value": old_value,
                "update_mask": update_mask
            }
        )

