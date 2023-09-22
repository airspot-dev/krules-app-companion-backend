from redis_om import HashModel, Field


class Channel(HashModel):

    document_id: str = Field(index=True)
    code: str
    name: str = Field(index=True)
    params: dict


class Trigger(HashModel):

    document_id: str = Field(index=True)
    channels: list
    entityFields: list
    event: list = Field(default=[])
    groupMatch: str
    name: str = Field(index=True)
    running: bool = Field(default=True)
