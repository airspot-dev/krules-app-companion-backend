import os
import re
from krules_fastapi_env import KRulesAPIRouter
# from redis_om import NotFoundError
from starlette.requests import Request
from google.events.cloud import firestore
import firebase_admin
from firebase_admin import firestore as firestore_client
from datetime import datetime, timezone, timedelta
from krules_core.providers import subject_factory
import logging
# import models

logger = logging.getLogger()

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")
ttl_regex = re.compile("^(?P<subscription>.+)[/]settings[/]schemas[/](?P<group>.+)$")
triggers_regex = re.compile("^(?P<subscription>.+)[/]settings[/]automations[/](?P<trigger>.+)$")
channels_regex = re.compile("^(?P<subscription>.+)[/]settings[/]channels[/](?P<channel>.+)$")

firebase_admin.initialize_app()
db = firestore_client.client()

router = KRulesAPIRouter(
    prefix="/eventSourcing",
    tags=["eventsourcing-archiver"],
    responses={404: {"description": "Not found"}},
)

DOCS_PATH = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/databases/{os.environ.get('FIRESTORE_DATABASE', '(default)')}/documents/"

# models.init()


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
    if int(os.environ.get("EVENT_SOURCING_DISABLED", "0")):
        return
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    collection = payload.value.name.replace(DOCS_PATH, "")
    match = collection_regex.match(collection)
    if match is not None:
        state = map_value_to_plain_dict(payload.value)
        if "old_value" in payload: # if old_value is not in payload document has just been created
            changed_properties = [el for el in list(payload.update_mask.field_paths) if not el.startswith("_")]
        else:
            changed_properties = [k for k in state.keys() if not k.startswith("_")]
        if len(changed_properties) == 0:
            return
        collection_info = match.groupdict()
        subscription = collection_info["subscription"]
        group = collection_info["group"]
        if "/" in group:
            return
        entity_id = collection_info["entity_id"]
        subject = subject_factory(f'schema|{subscription}|{group}', use_cache_default=False)
        if "ttl" in subject:
            ttl = {k: int(v) for k, v in subject.get("ttl").items()}
        else:
            ttl = {"hours": 1}
        _, doc_ref = db.collection(f"{subscription}/groups/{group}/{entity_id}/event_sourcing").add({
                "datetime": datetime.now(timezone.utc),
                "expire_date": datetime.now(timezone.utc) + timedelta(**ttl),
                "entity_id": entity_id,
                "state": state,
                "changed_properties": changed_properties,
            }
        )


@router.post("/ttl")
async def set_ttl(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    collection = payload.value.name.replace(DOCS_PATH, "")
    match = ttl_regex.match(collection)
    logger.info(f"####### MATCH: {match}")
    logger.info(f"####### COLLECTION: {payload.value.name}")
    logger.info(f"####### PAYLOAD: {map_value_to_plain_dict(payload.value)}")
    if match is not None:
        group_info = match.groupdict()
        subscription = group_info["subscription"]
        group_name = group_info["group"]
        subject = subject_factory(f'schema|{subscription}|{group_name}', use_cache_default=False)
        settings = map_value_to_plain_dict(payload.value)
        ttl = settings.get("ttl", None)
        if ttl:
            subject.set("ttl", ttl, muted=True)


# @router.post("/sync/triggers")
# async def sync_triggers_and_channels(request: Request):
#     raw_pb = await request.body()
#     payload = firestore.DocumentEventData.deserialize(raw_pb)
#     collection = payload.value.name.replace(DOCS_PATH, "")
#     match = triggers_regex.match(collection)
#     if match is not None:
#         trigger_info = match.groupdict()
#         subscription = trigger_info["subscription"]
#         trigger_id = trigger_info["trigger"]
#         document_id = f"{subscription}/{trigger_id}"
#         trigger_obj = map_value_to_plain_dict(payload.value)
#         try:
#             trigger = models.Trigger.get(document_id)
#             changed_properties = [el for el in list(payload.update_mask.field_paths) if not el.startswith("_")]
#             for prop in changed_properties:
#                 setattr(trigger, prop, trigger_obj[prop])
#         except NotFoundError:
#             models.Trigger(
#                 document_id=document_id,
#                 channels=trigger_obj["channels"],
#                 entityFields=trigger_obj["entityFields"],
#                 event=trigger_obj["event"],
#                 groupMatch=trigger_obj["groupMatch"],
#                 name=trigger_obj["name"],
#                 running=trigger_obj["running"],
#             ).save()



routers = [router]
