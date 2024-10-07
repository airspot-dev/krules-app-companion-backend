import logging
import os
import re

from fastapi import APIRouter
from google.events.cloud import firestore
from google.events.cloud.firestore_v1 import DocumentEventData
from krules_core.providers import event_router_factory
from krules_core.providers import subject_factory
from starlette.requests import Request

from common.event_types import SystemEventsV1

logger = logging.getLogger()

collection_regex = re.compile("^(?P<subscription>.+)[/]groups[/](?P<group>.+)[/](?P<entity_id>.+)$")
schema_regex = re.compile("^(?P<subscription>.+)[/]settings[/]schemas[/](?P<group>.+)$")
channel_regex = re.compile("^(?P<subscription>.+)[/]settings[/]channels[/](?P<channel_id>.+)$")
triggers_regex = re.compile("^(?P<subscription>.+)[/]settings[/]automations[/](?P<trigger_id>.+)$")

# firebase_admin.initialize_app()
# db = firestore_client.client()

entities_router = APIRouter(
    prefix="/entities",
    tags=["firestore-entity-updates"],
    responses={404: {"description": "Not found"}},
)

schemas_router = APIRouter(
    prefix="/schemas",
    tags=["firestore-schemas-updates"],
    responses={404: {"description": "Not found"}},
)

channels_router = APIRouter(
    prefix="/channels",
    tags=["firestore-channels-updates"],
    responses={404: {"description": "Not found"}},
)

triggers_router = APIRouter(
    prefix="/triggers",
    tags=["firestore-triggers-updates"],
    responses={404: {"description": "Not found"}},
)

settings_router = APIRouter(
    prefix="/settings",
    tags=["firestore-settings-updates"],
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
        state = map_value_to_plain_dict(payload.value)
        old_state = map_value_to_plain_dict(payload.old_value)
        changed_properties = [el for el in changed_properties if not el.startswith("_")]
        if event_type == SystemEventsV1.ENTITY_CREATED:
            changed_properties = list(state.keys())
        collection_info = match.groupdict()
        subscription = collection_info["subscription"]
        group = collection_info["group"]
        if "/" in group:
            return
        entity_id = collection_info["entity_id"]
        subject = subject_factory(f'entity|{subscription}|{group}|{entity_id}')
        payload = dict(
            subscription=subscription,
            group=group,
            id=entity_id,
            changed_properties=changed_properties,
            state=state,
            old_state=old_state,
        )
        event_router.route(
            event_type,
            subject=subject,
            payload=payload,
            topic=os.environ["FIRESTORE_UPDATES_TOPIC"],
            subscription=subscription,
            group=group
        )


@entities_router.post("")
async def entity_written(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    event_type = SystemEventsV1.ENTITY_UPDATED
    if not bool(payload.old_value):
        event_type = SystemEventsV1.ENTITY_CREATED
    elif not bool(payload.value):
        event_type = SystemEventsV1.ENTITY_DELETED
    _process_entity_event(payload, event_type)


@schemas_router.post("")
async def schema_written(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    collection = payload.value.name.replace(DOCS_PATH, "")
    match = schema_regex.match(collection)
    if match is None:
        collection = payload.old_value.name.replace(DOCS_PATH, "")
        match = schema_regex.match(collection)
    if match is not None:
        event_type = SystemEventsV1.SCHEMA_UPDATED
        if not bool(payload.old_value):
            event_type = SystemEventsV1.SCHEMA_CREATED
        elif not bool(payload.value):
            event_type = SystemEventsV1.SCHEMA_DELETED
        group_info = match.groupdict()
        subscription = group_info["subscription"]
        group = group_info["group"]
        subject = subject_factory(f'schema|{subscription}|{group}')
        v_payload = {}
        if event_type in (SystemEventsV1.SCHEMA_CREATED, SystemEventsV1.SCHEMA_UPDATED):
            v_payload = map_value_to_plain_dict(payload.value)
        elif event_type == SystemEventsV1.SCHEMA_DELETED:
            v_payload = map_value_to_plain_dict(payload.old_value)
        event_router.route(
            event_type=event_type,
            subject=subject,
            payload=v_payload,
            topic=os.environ["SETTINGS_TOPIC"],
            subscription=subscription,
            group=group
        )


@channels_router.post("")
async def channel_written(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    collection = payload.value.name.replace(DOCS_PATH, "")
    match = channel_regex.match(collection)
    if not match:
        collection = payload.old_value.name.replace(DOCS_PATH, "")
        match = channel_regex.match(collection)
    if match:
        event_type = SystemEventsV1.CHANNEL_UPDATED
        if not bool(payload.old_value):
            event_type = SystemEventsV1.CHANNEL_CREATED
        elif not bool(payload.value):
            event_type = SystemEventsV1.CHANNEL_DELETED
        group_info = match.groupdict()
        subscription = group_info["subscription"]
        channel_id = group_info["channel_id"]
        subject = subject_factory(f'channel|{subscription}|{channel_id}')
        v_payload = {}
        if event_type in (SystemEventsV1.CHANNEL_CREATED, SystemEventsV1.CHANNEL_UPDATED):
            v_payload = map_value_to_plain_dict(payload.value)
        elif event_type == SystemEventsV1.CHANNEL_DELETED:
            v_payload = map_value_to_plain_dict(payload.old_value)
        event_router.route(
            event_type=event_type,
            subject=subject,
            payload=v_payload,
            topic=os.environ["SETTINGS_TOPIC"],
            subscription=subscription,
        )


@triggers_router.post("")
async def trigger_written(request: Request):
    raw_pb = await request.body()
    payload = firestore.DocumentEventData.deserialize(raw_pb)
    collection = payload.value.name.replace(DOCS_PATH, "")
    match = triggers_regex.match(collection)
    if not match:
        collection = payload.old_value.name.replace(DOCS_PATH, "")
        match = triggers_regex.match(collection)
    if match:
        event_type = SystemEventsV1.TRIGGER_UPDATED
        if not bool(payload.old_value):
            event_type = SystemEventsV1.TRIGGER_CREATED
        elif not bool(payload.value):
            event_type = SystemEventsV1.TRIGGER_DELETED
        group_info = match.groupdict()
        subscription = group_info["subscription"]
        trigger_id = group_info["trigger_id"]
        subject = subject_factory(f'trigger|{subscription}|{trigger_id}')
        v_payload = {}
        if event_type in (SystemEventsV1.TRIGGER_CREATED, SystemEventsV1.TRIGGER_UPDATED):
            v_payload = map_value_to_plain_dict(payload.value)
        elif event_type == SystemEventsV1.TRIGGER_DELETED:
            v_payload = map_value_to_plain_dict(payload.old_value)
        event_router.route(
            event_type=event_type,
            subject=subject,
            payload=v_payload,
            topic=os.environ["SETTINGS_TOPIC"],
            subscription=subscription,
        )



