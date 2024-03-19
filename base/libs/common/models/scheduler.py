import random
from abc import ABC
from datetime import datetime, timedelta
from typing import List, Tuple, Any

from krules_core.providers import subject_factory
from pydantic import BaseModel, PositiveInt, model_validator, field_serializer, Field, computed_field, field_validator

from common.event_types import SystemEventsV1
from common.models.entities import EntityEvent


class ScheduleCallbackBase(BaseModel):
    when: datetime | None = None
    rnd_delay: int | None = None
    seconds: PositiveInt | None = None
    now: bool | None = None
    channels: List[str] = []
    message: str | None = None
    fresh_data: bool | None = False

    @model_validator(mode='after')
    def validate_all(self) -> 'ScheduleCallbackBase':
        assert sum(p is not None for p in [self.when, self.seconds, self.now]) == 1, "Specify one of when, seconds, now"
        assert len(self.channels) > 0, "At least one channel must be specified"

        return self

    def get_eta(self, ignore_delay=False):
        if self.when is not None:
            eta = self.when
        else:
            eta = datetime.now()
            if self.seconds is not None:
                eta = eta + timedelta(seconds=self.seconds)
        if not ignore_delay and self.rnd_delay is not None and self.rnd_delay > 0:
            eta += timedelta(seconds=random.randint(0, self.rnd_delay))
        return eta


class ScheduleCallbackSingleRequest(ScheduleCallbackBase):
    replace_id: str | None = None

    def get_task(
            self,
            subscription: PositiveInt,
            group: str,
            entity_id: str,
            task_id: str = None,
    ) -> 'ScheduleEntityTask':
        return ScheduleEntityTask(
            task_id=task_id,
            eta=self.get_eta(),
            channels=self.channels,
            message=self.message,
            replace_id=self.replace_id,
            subscription=subscription,
            group=group,
            entity_id=entity_id,
        )


class ScheduleCallbackMultiRequest(ScheduleCallbackBase):
    filter: Tuple[str, str, Any] | None = None

    def get_task(
            self,
            subscription: PositiveInt,
            group: str,
            task_id: str = None,
    ) -> 'ScheduleGroupTask':
        return ScheduleGroupTask(
            task_id=task_id,
            eta=self.get_eta(ignore_delay=True),
            channels=self.channels,
            message=self.message,
            subscription=subscription,
            group=group,
            filter=self.filter,
            task_rnd_delay=self.rnd_delay,
            fresh_data=self.fresh_data
        )


class ScheduleTaskBase(BaseModel):
    task_id: str | None = None
    eta: datetime
    channels: List[str] = []
    message: str | None = None
    fresh_data: bool | None = False


class ScheduleEntityTask(ScheduleTaskBase):
    subscription: int
    group: str
    entity_id: str
    replace_id: str | None = None

    # @model_validator(mode='after')
    # def validate_all(self) -> 'ScheduleEntityTask':
    #     if self.replace_id is not None:
    #         assert self.replace_id.startswith(f"{self.subscription}|")
    #     return self


class ScheduleGroupTask(ScheduleTaskBase):
    subscription: int
    group: str
    filter: Tuple[str, str, Any] | None = None
    task_rnd_delay: int | None = 0


class SchedulablePayload(BaseModel, ABC):
    type: str = Field(exclude=True)
    subject: str = Field(exclude=True)
    subscription: int


class SchedulerCallbackPayload(SchedulablePayload):
    type: str = Field(SystemEventsV1.ENTITY_CALLBACK, exclude=True)

    last_updated: datetime
    task_id: str
    group: str
    id: str
    state: dict
    message: str

    @field_serializer('last_updated')
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()

    @model_validator(mode='before')
    def validate_mode(cls, values):
        if "subject" not in values:
            values["subject"] = f"entity|{values.get('subscription')}|{values.get('group')}|{values.get('id')}"
        return values


class EntityUpdatedCallbackPayload(SchedulablePayload, EntityEvent[dict]):

    @model_validator(mode='before')
    def validate_subject(cls, values):
        if "subject" not in values:
            values["subject"] = f"entity|{values.get('subscription')}|{values.get('group')}|{values.get('id')}"
        return values
