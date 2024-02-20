import abc
import os
from typing import Callable

import requests
from cloudevents.conversion import to_binary
from cloudevents.http import CloudEvent
from krules_core.providers import event_router_factory
from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

from common.event_types import SystemEventsV1
from common.models.scheduler import SchedulerCallbackPayload, SchedulablePayload

supported_channels = {
    'pub_sub': 'PubSubChannelImpl',
    'webhook': 'WebhookChannelImpl',
}


class ChannelImpl(BaseModel, abc.ABC):
    @abc.abstractmethod
    def send(self, payload: SchedulablePayload, exception_handler: Callable):
        pass


class Channel(BaseModel):
    code: str
    name: str
    params: dict
    slug: str

    @field_validator('code')
    @classmethod
    def validata_code(cls, v: str, info: ValidationInfo) -> str:
        global supported_channels
        assert v in supported_channels, f"unsupported channel type '{v}'. valids: {supported_channels}"
        return v

    def implementation(self) -> ChannelImpl:
        return eval(supported_channels[self.code])(
            **self.params
        )


class PubSubChannelImpl(ChannelImpl):
    topic: str

    def send(self, payload: SchedulablePayload, exception_handler: Callable):
        event_router_factory().route(
            # SystemEventsV1.ENTITY_CALLBACK,
            payload.type,
            #f"entity|{payload.subscription}|{payload.group}|{payload.id}",
            payload.subject,
            payload.model_dump(),
            topic=self.topic,
            exception_handler=exception_handler
        )


class WebhookChannelImpl(ChannelImpl):
    url: str
    headers: dict = {}

    def send(self, payload: SchedulablePayload, exception_handler: Callable):
        attributes = {
            #"type": SystemEventsV1.ENTITY_CALLBACK,
            "type": payload.type,
            #"subject": f"entity|{payload.subscription}|{payload.group}|{payload.id}",
            "subject": payload.subject,
            "source": os.environ["CE_SOURCE"]
        }
        attributes.update(
            {f"x{k.replace('-', '')}": v for k, v in self.headers.items()}
        )
        data = payload.model_dump()
        event = CloudEvent(attributes, data)

        # Creates the HTTP request representation of the CloudEvent in structured content mode
        headers, body = to_binary(event)
        headers.update(
            self.headers
        )

        try:
            response = requests.post(self.url, data=body, headers=headers)
            response.raise_for_status()
        except Exception as e:
            exception_handler(e)
