from typing import List, Mapping, ClassVar, Dict

from pydantic import BaseModel, field_validator

from common.event_types import SystemEventsV1
from common.models.entities import EntityEvent

from fnmatch import fnmatch


class Trigger(BaseModel):
    name: str
    groupMatch: str = "*"
    channels: List[str]
    entityFields: List[str]
    events: List[str]
    running: bool

    EVENTS_TRANSFORMATION_MAP: ClassVar[Dict[str, str]] = {
        'onEntityCreated': SystemEventsV1.ENTITY_CREATED,
        'onEntityUpdated': SystemEventsV1.ENTITY_UPDATED,
        'onEntityDeleted': SystemEventsV1.ENTITY_DELETED,
    }

    def __init__(self, **data):
        values = data.get('events') or data.get('event')  # Alias
        data['events'] = self.check_and_transform_events(values)
        super().__init__(**data)

    @classmethod
    #@field_validator('events', mode='before')
    def check_and_transform_events(cls, values):
        return [cls.EVENTS_TRANSFORMATION_MAP.get(value, value) for value in values]

        # Custom validator for the 'events' field
    # @classmethod
    # @field_validator('events')
    # def check_events_alias(cls, value, values, field, config):
    #     if 'event' in values:
    #         # If 'event' key exists, use its value for 'events'
    #         return values['event']
    #     elif 'events' in values:
    #         # If 'events' key exists, use its value
    #         return values['events']
    #     else:
    #         # Raise an error if neither key is present
    #         raise ValueError("Either 'event' or 'events' must be provided")

    def applies_to(self, event: EntityEvent) -> bool:

        print("Checking if trigger applies to GROUP, self.groupMatch: ", self.groupMatch)
        print("Checking if trigger applies to GROUP, event.group: ", event.group)
        if self.groupMatch != "*" and not fnmatch(event.group, self.groupMatch):
            print("Group does not match")
            return False

        print("Checking if trigger applies to EVENTS, self.events: ", self.events)
        print("Checking if trigger applies to EVENTS, event.type: ", event.type)
        if event.type not in self.events:
            print("Event does not match")
            return False

        print("Checking if trigger applies to PROPERTIES, self.entityFields: ", self.entityFields)
        print("Checking if trigger applies to PROPERTIES, event.changed_properties: ", event.changed_properties)
        if not len(self.entityFields) == 0 and not any(item in event.changed_properties for item in self.entityFields):
            print("Properties do not match")
            return False

        print("Trigger applies")

        return True


class Subscription(BaseModel):
    triggers: Mapping[str, Trigger]
