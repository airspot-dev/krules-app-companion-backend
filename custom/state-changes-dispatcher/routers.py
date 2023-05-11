import os
import re
from krules_fastapi_env import KRulesAPIRouter
from starlette.requests import Request
from google.events.cloud import firestore

from krules_core.providers import event_router_factory

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")

event_router = event_router_factory()


router = KRulesAPIRouter(
    prefix="/wb",
    tags=["wb-dispatcher"],
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
    # print(collection)
    match = collection_regex.match(collection)
    if match is not None:
        collection_info = match.groupdict()
        subscription = collection_info["subscription"]
        group = collection_info["group"]
        entity_id = collection_info["entity_id"]
        event_router.route(
            event_type="entity-state-changed",
            subject=f"entity|{subscription}|{group}|{entity_id}",
            payload={
                "entity_id": entity_id,
                "group": group,
                "subscription": int(subscription),
                # "raw": str(raw_pb),
                "value": map_value_to_plain_dict(payload.value),
                "old_value": map_value_to_plain_dict(payload.old_value),
                "update_mask": list(payload.update_mask.field_paths)
            }
        )

routers = [router]
