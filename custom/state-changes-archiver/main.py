import re
import os
from datetime import datetime, timezone

import google.auth
import firebase_admin
from firebase_admin import firestore

_, project = google.auth.default()

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")
docs_path = f"projects/{project}/databases/{os.environ.get('FIRESTORE_DATABASE', '(default)')}/documents/"

firebase_admin.initialize_app()


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


def index(data, context):
    """ Triggered by a change to a Firestore document.
    Args:
        data (dict): The event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """

    collection = context.resource.replace(docs_path, "")
    match = collection_regex.match(collection)
    info = match.groupdict()
    update_mask = data["updateMask"]["fieldPaths"]
    update_mask.remove("LAST_UPDATE")
    db = firestore.client()
    print(f"@@@@@@@ DATA: {data}")
    _, doc_ref = db.collection(
        f"{info['subscription']}/groups/{info['group']}/{info['entity_id']}/event_sourcing"
    ).add(
        {
            "datetime": datetime.now(timezone.utc).isoformat(),
            "entity_id": info['entity_id'],
            "state": map_value_to_plain_dict(data["value"]),
            "changed_properties": update_mask,
        }
    )
