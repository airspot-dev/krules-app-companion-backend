import logging
import os
import re

from google.events.cloud import firestore
from google.events.cloud.firestore_v1 import DocumentEventData
from krules_core.providers import event_router_factory
from krules_core.providers import subject_factory
from krules_fastapi_env import KRulesAPIRouter
from starlette.requests import Request

from common.event_types import SystemEventsV1

logger = logging.getLogger()

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")
schema_regex = re.compile("^(?P<subscription>.+)[/]settings[/]schemas[/](?P<group>.+)$")

# firebase_admin.initialize_app()
# db = firestore_client.client()

entities_router = KRulesAPIRouter(
    prefix="/entities",
    tags=["firestore-entitiy-updates"],
    responses={404: {"description": "Not found"}},
)

schemas_router = KRulesAPIRouter(
    prefix="/schemas",
    tags=["firestore-schema-updates"],
    responses={404: {"description": "Not found"}},
)

DOCS_PATH = f"{os.environ['FIRESTORE_ID']}/documents/"

event_router = event_router_factory()


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
    elif "integer_value" in raw:
        value = int(value)
    return value


def map_value_to_plain_dict(obj):
    plain_dict = {}
    for k in [k for k in obj.fields if not k.startswith("_")]:
        plain_dict[k] = get_value(obj.fields.get(k))
    return plain_dict


def _process_entity_event(payload: DocumentEventData, event_type: SystemEventsV1):

    collection_value = SystemEventsV1.ENTITY_DELETED and payload.old_value or payload.value
    collection = collection_value.name.replace(DOCS_PATH, "")
    match = collection_regex.match(collection)
    if match is not None:
        changed_properties = [el for el in list(payload.update_mask.field_paths)]
        if "_deleting" in changed_properties and event_type == SystemEventsV1.ENTITY_UPDATED:
            # entity has been changed just because marked for deleting
            return
        changed_properties = [el for el in changed_properties if not el.startswith("_")]
        collection_info = match.groupdict()
        subscription = collection_info["subscription"]
        group = collection_info["group"]
        if "/" in group:
            return
        entity_id = collection_info["entity_id"]
        subject = subject_factory(f'entity|{subscription}|{group}|{entity_id}')
        payload=dict(
                subscription=subscription,
                group=group,
                entity_id=entity_id,
                changed_properties=changed_properties,
                state=map_value_to_plain_dict(payload.value),
                old_state=map_value_to_plain_dict(payload.old_value),
            )
        event_router.route(
            event_type,
            subject=subject,
            payload=payload,
            topic=os.environ["FIRESTORE_UPDATES_TOPIC"],
            subscription=subscription,
            group=group
        )


@entities_router.post("/created")
async def document_created(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    _process_entity_event(payload, SystemEventsV1.ENTITY_CREATED)


@entities_router.post("/updated")
async def document_updated(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    _process_entity_event(payload, SystemEventsV1.ENTITY_UPDATED)


@entities_router.post("/deleted")
async def document_deleted(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    _process_entity_event(payload, SystemEventsV1.ENTITY_DELETED)

# @entities_router.post("/written")
# async def document_written(request: Request):
#     raw_pb = await request.body()
#     payload = firestore.DocumentEventData.deserialize(raw_pb)
#     print(str(request.values()))
#     print(str(request.items()))
#     print(str(payload).replace("\n", " "))


@schemas_router.post("")
async def schema_updates(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    collection = payload.value.name.replace(DOCS_PATH, "")
    match = schema_regex.match(collection)
    if match is not None:
        group_info = match.groupdict()
        subscription = group_info["subscription"]
        group = group_info["group"]
        subject = subject_factory(f'schema|{subscription}|{group}')
        settings = map_value_to_plain_dict(payload.value)
        event_router.route(
            SystemEventsV1.SCHEMA_UPDATED,
            subject=subject,
            payload=settings,
            topic=os.environ["SETTINGS_TOPIC"],
            subscription=subscription,
            group=group
        )

        # ttl = settings.get("ttl", None)
        # if ttl:
        #     subject.set("ttl", ttl, muted=True)


routers = [entities_router, schemas_router]
