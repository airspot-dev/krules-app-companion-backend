from pydantic import BaseModel, Field


class Trigger(BaseModel):

    name: str
    channels: list[str]
    entityFields: list[str]
    events: list[str] = Field(..., validation_alias='event')
