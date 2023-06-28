import os
import re
from krules_fastapi_env import KRulesAPIRouter
from starlette.requests import Request
from google.events.cloud import firestore
import firebase_admin
from firebase_admin import firestore as firestore_client
from datetime import datetime, timezone, timedelta
from krules_core.providers import subject_factory

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")
ttl_regex = re.compile("^(?P<subscription>.+)[/]settings[/]schemas[/](?P<group>.+)$")

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
    if int(os.environ.get("EVENT_SOURCING_DISABLED", "0")):
        return
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    docs_path = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/databases/{os.environ.get('FIRESTORE_DATABASE', '(default)')}/documents/"
    collection = payload.value.name.replace(docs_path, "")
    match = collection_regex.match(collection)
    if match is not None:
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
            ttl = {"hours": 24}
            subject.set("ttl", ttl, muted=True)
        # try:
            # settings = db.document(f"{subscription}/settings/schemas/{group}").get()
            # if settings is not None:
            #     settings = settings.to_dict()
            #     ttl = settings.get("ttl", {"hours": 24})
            # else:
            #     ttl = {"hours": 24}
        _, doc_ref = db.collection(f"{subscription}/groups/{group}/{entity_id}/event_sourcing").add({
                "datetime": datetime.now(timezone.utc),
                "expire_date": datetime.now(timezone.utc) + timedelta(**ttl),
                "entity_id": entity_id,
                "state": map_value_to_plain_dict(payload.value),
                "changed_properties": [el for el in list(payload.update_mask.field_paths) if el != "LAST_UPDATE"],
            }
        )
        # except Exception as ex:
        #     raise ex

import logging

logger = logging.getLogger()

@router.post("/ttl")
async def set_ttl(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    docs_path = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/databases/{os.environ.get('FIRESTORE_DATABASE', '(default)')}/documents/"
    collection = payload.value.name.replace(docs_path, "")
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


routers = [router]
