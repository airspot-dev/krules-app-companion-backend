
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

    ENTITY_CALLBACK = EventType(f"{PREFIX}.entity.v1.callback")
    ENTITY_CREATED = EventType(f"{PREFIX}.entity.v1.created")
    ENTITY_DELETED = EventType(f"{PREFIX}.entity.v1.deleted")
    ENTITY_UPDATED = EventType(f"{PREFIX}.entity.v1.updated")
    GROUP_CREATED = EventType(f"{PREFIX}.group.v1.created")
    GROUP_DELETED = EventType(f"{PREFIX}.group.v1.deleted")
    SCHEMA_UPDATED = EventType(f"{PREFIX}.settings.schema.v1.updated")
