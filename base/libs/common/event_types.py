
from krules_core.models import EventType

PREFIX = "io.krules.streams"


class IngestionEventsV1:

    ENTITY_DATA = EventType(f"{PREFIX}.entity.v1.data")
    ENTITY_DELETE = EventType(f"{PREFIX}.entity.v1.delete")
    ENTITY_SCHEDULE = EventType(f"{PREFIX}.entity.v1.schedule")
    GROUP_DATA = EventType(f"{PREFIX}.group.v1.data")
    GROUP_DELETE = EventType(f"{PREFIX}.group.v1.delete")
    GROUP_SCHEDULE = EventType(f"{PREFIX}.group.v1.schedule")


class SystemEventsV1:

    #ENTITY_CALLBACK = EventType(f"{PREFIX}.entity.v1.callback")
    #GROUP_CALLBACK = EventType(f"{PREFIX}.group.v1.callback")
    ENTITY_CREATED = EventType(f"{PREFIX}.entity.v1.created")
    ENTITY_DELETED = EventType(f"{PREFIX}.entity.v1.deleted")
    ENTITY_UPDATED = EventType(f"{PREFIX}.entity.v1.updated")
    #GROUP_CREATED = EventType(f"{PREFIX}.group.v1.created")
    #GROUP_DELETED = EventType(f"{PREFIX}.group.v1.deleted")
    SCHEMA_CREATED = EventType(f"{PREFIX}.settings.schema.v1.created")
    SCHEMA_UPDATED = EventType(f"{PREFIX}.settings.schema.v1.updated")
    SCHEMA_DELETED = EventType(f"{PREFIX}.settings.schema.v1.deleted")
    CHANNEL_CREATED = EventType(f"{PREFIX}.settings.channel.v1.created")
    CHANNEL_UPDATED = EventType(f"{PREFIX}.settings.channel.v1.updated")
    CHANNEL_DELETED = EventType(f"{PREFIX}.settings.channel.v1.deleted")
