import os
import re
from krules_fastapi_env import KRulesAPIRouter
from starlette.requests import Request
from google.events.cloud import firestore
import firebase_admin
from firebase_admin import firestore as firestore_client
from datetime import datetime, timezone

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")

firebase_admin.initialize_app()
db = firestore_client.client()

router = KRulesAPIRouter(
    prefix="/eventSourcing",
    tags=["eventsourcing-archiver"],
    responses={404: {"description": "Not found"}},
)


def get_value(obj):
    raw = firestore.Value.to_dict(obj)
    value = list(raw.values())[0]
    if "array_value" in raw:
        value = []
        for el in obj.array_value.values:
            value.append(get_value(el))
    elif "map_value" in raw:
        value = map_value_to_plain_dict(obj.map_value)
    elif "null_value" in raw:
        return None
    return value


def map_value_to_plain_dict(obj):
    plain_dict = {}
    for k in obj.fields:
        plain_dict[k] = get_value(obj.fields.get(k))
    return plain_dict


@router.post("")
async def dispatch(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    docs_path = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/databases/{os.environ.get('FIRESTORE_DATABASE', '(default)')}/documents/"
    collection = payload.value.name.replace(docs_path, "")
    print(f"@@@@@@@ collection: {collection}")
    match = collection_regex.match(collection)
    if match is not None:
        collection_info = match.groupdict()
        subscription = collection_info["subscription"]
        group = collection_info["group"]
        if "/" in group:
            return
        entity_id = collection_info["entity_id"]
        state = map_value_to_plain_dict(payload.value)
        try:
            _, doc_ref = db.collection(f"{subscription}/groups/{group}/{entity_id}/event_sourcing").add({
                    "datetime": datetime.now(timezone.utc).isoformat(),
                    "entity_id": entity_id,
                    "state": map_value_to_plain_dict(payload.value),
                    "changed_properties": [el for el in list(payload.update_mask.field_paths) if el != "LAST_UPDATE"],
                }
            )
        except Exception as ex:
            print(f"@@@@@@@ collection_info: {collection_info}")
            print(f"###### state : {state}")
            raise ex

routers = [router]
