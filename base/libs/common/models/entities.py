from enum import Enum
from typing import Generic, Sequence, TypeVar, Literal

from pydantic import BaseModel, validator, field_validator, ValidationError

from common.event_types import SystemEventsV1

T = TypeVar("T")


class EntityEventType(str, Enum):
    CREATED = SystemEventsV1.ENTITY_CREATED
    UPDATED = SystemEventsV1.ENTITY_UPDATED
    DELETED = SystemEventsV1.ENTITY_DELETED


class EntityEvent(BaseModel, Generic[T]):
    type: EntityEventType
    id: str
    group: str
    subscription: str
    changed_properties: Sequence[str]
    state: T | None = None
    old_state: T | None = None

    @classmethod
    @field_validator('type')
    def validate_event_type(cls, value):
        try:
            return EntityEventType(value)
        except ValueError:
            raise ValidationError(f"Invalid event type: {value}")


