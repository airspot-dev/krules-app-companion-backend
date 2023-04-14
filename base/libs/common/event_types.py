from krules_core.models import EventType

ENTITY_PROPERTY_CHANGED = EventType("sys.entity.propertyChanged")
ENTITY_STATE_CHANGED = EventType("sys.entity.stateChanged")
SUBJECT_PROPERTIES_DATA = EventType("subject.properties.data")
SUBJECT_PROPERTIES_DATA_MULTI = EventType("subject.properties.data.multi")
RESET_SCHEMA = EventType("reset-schema")
