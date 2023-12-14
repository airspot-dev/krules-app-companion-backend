import uuid
from typing import Optional

import os
import uuid
from typing import Optional

import firebase_admin
import google.auth.exceptions
import google.auth.transport.requests
import google.oauth2.id_token
import pysnooper
import requests
from fastapi import Security, HTTPException, Depends
from fastapi.openapi.models import APIKey
from fastapi.security.api_key import APIKeyHeader
from krules_core.providers import event_router_factory
from krules_fastapi_env import KRulesAPIRouter
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from common.event_types import IngestionEventsV1
from common.models.scheduler import ScheduleCallbackSingleRequest, ScheduleCallbackMultiRequest
from env import get_secret

firebase_admin.initialize_app()

router = KRulesAPIRouter(
    prefix="/api/v1",
    tags=["apiV1"],
    responses={404: {"description": "Not found"}},
)

scheduler = KRulesAPIRouter(
    prefix="/api/scheduler/v1",
    tags=["apiSchedulerV1"],
    responses={404: {"description": "Not found"}},
)

GOOGLE_HTTP_REQUEST = google.auth.transport.requests.Request()

api_key_header = APIKeyHeader(name="api-key", auto_error=False)
firestore_token_header = APIKeyHeader(name="Authorization", auto_error=False)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

INGESTION_TOPIC = os.environ["INGESTION_TOPIC"]
SCHEDULER_TOPIC = os.environ["SCHEDULER_TOPIC"]


async def get_api_key(header: str = Security(api_key_header)):
    api_key = get_secret("INGESTION_API_KEY")
    if header == api_key:
        return header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


async def check_firebase_user(header: str = Security(firestore_token_header),
                              api_key_header: str = Security(api_key_header)):
    api_key = get_secret("INGESTION_API_KEY")

    if api_key_header == api_key:
        return header
    else:
        if not header:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Authorization header missing"
            )
        id_token = header.split(' ').pop()
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, GOOGLE_HTTP_REQUEST, audience=os.environ.get('FIRESTORE_PROJECT_ID')
            )
        except google.auth.exceptions.InvalidValue as ex:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail=str(ex)
            )
        except google.auth.exceptions.MalformedError as ex:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=str(ex)
            )

        if not claims:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate authorization token"
            )
        else:
            return claims


class GroupUpdatePayload(BaseModel):
    data: dict
    entities_filter: Optional[list | None]



class ScheduleCallbackResponsePayload(BaseModel):
    task_id: Optional[str | None]


class ActiveSubscriptionPayload(BaseModel):
    active_subscription: int


# @router.get("/user/subscriptions", summary="Get user subscriptions")
# async def get_user_subscriptions(token: APIKey = Security(firestore_token_header)):
#     if token is None:
#         raise HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate authorization token"
#         )
#     print(f"#################### {token}")
#     resp = requests.get(
#         "http://firebase-users-handler/user/subscriptions",
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     resp.raise_for_status()
#     return resp.json()
#
#
# @router.post("/user/subscriptions/activate", summary="Set active subscription")
# async def activate_subscription(payload: ActiveSubscriptionPayload, token: APIKey = Security(firestore_token_header)):
#     if token is None:
#         raise HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate authorization token"
#         )
#
#     resp = requests.post(
#         "http://firebase-users-handler/user/subscriptions/activate",
#         json=payload,
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     resp.raise_for_status()
#     return resp.json()


@router.delete("/{subscription}/{group}", summary="Delete group")
async def delete_group(subscription, group: str, token: APIKey = Depends(check_firebase_user)):
    event_router_factory().route(
        subject=f'group|{subscription}|{group}',
        event_type=IngestionEventsV1.GROUP_DELETE,
        payload={
            "token": token
        },
        topic=INGESTION_TOPIC,
    )


@router.delete("/{subscription}/{group}/{entity_id}", summary="Delete entity")
async def delete_entity(subscription, group, entity_id: str, token: APIKey = Depends(check_firebase_user)):
    event_router_factory().route(
        subject=f'entity|{subscription}|{group}|{entity_id}',
        event_type=IngestionEventsV1.ENTITY_DELETE,
        payload={
            "token": token
        },
        topic=INGESTION_TOPIC,
    )


@router.post("/{subscription}/{group}")
async def ingestion_data_multi(subscription, group, body: GroupUpdatePayload, api_key: APIKey = Depends(get_api_key)):
    # data = await request.json()
    if body.entities_filter is None:
        body.entities_filter = []
    event_router_factory().route(
        subject=f'group|{subscription}|{group}',
        event_type=IngestionEventsV1.GROUP_DATA,
        payload={
            "data": body.data,
            "entities_filter": body.entities_filter,
        },
        topic=INGESTION_TOPIC,
    )


@router.post("/{subscription}/{group}/{entity_id}")
async def ingestion_data(subscription, group, entity_id, data: dict, api_key: APIKey = Depends(get_api_key)):
    # data = await request.json()
    event_router_factory().route(
        subject=f'entity|{subscription}|{group}|{entity_id}',
        event_type=IngestionEventsV1.ENTITY_DATA,
        payload={
            "data": data
        },
        topic=INGESTION_TOPIC,
    )


async def _schedule_request_base_check(body):
    tt_sum = sum(p is not None for p in [body.when, body.seconds, body.now])
    if tt_sum == 0 or tt_sum > 1:
        raise HTTPException(status_code=400, detail="You must specify only one from when, seconds or now")
    channels = body.channels
    if len(channels) == 0:
        raise HTTPException(status_code=400, detail="You must specify at least one channel")
    data = body.dict()
    when = data.get("when")
    if when is not None:
        data["when"] = when.isoformat()
    return data


@scheduler.post("/{subscription}/{group}/{entity_id}")
async def schedule_callback(subscription, group, entity_id, body: ScheduleCallbackSingleRequest,
                            api_key: APIKey = Depends(get_api_key)) -> ScheduleCallbackResponsePayload:
    task_id = f"{subscription}|{str(uuid.uuid4())}"

    event_router_factory().route(
        subject=f'entity|{subscription}|{group}|{entity_id}',
        event_type=IngestionEventsV1.ENTITY_SCHEDULE,
        payload={
            "task_id": task_id,
            "data": body.model_dump()
        },
        topic=SCHEDULER_TOPIC,
    )

    return ScheduleCallbackResponsePayload(task_id=task_id)


@scheduler.post("/{subscription}/{group}")
async def schedule_callback_multi(subscription, group, body: ScheduleCallbackMultiRequest,
                                  api_key: APIKey = Depends(get_api_key)) -> ScheduleCallbackResponsePayload:

    #with pysnooper.snoop(watch=('body.rnd_delay',)):
    task_id = f"{subscription}|{str(uuid.uuid4())}"
    data = body.model_dump()

    event_router_factory().route(
        subject=f'group|{subscription}|{group}',
        event_type=IngestionEventsV1.GROUP_SCHEDULE,
        payload={
            "task_id": task_id,
            "data": data
        },
        topic=SCHEDULER_TOPIC,
    )

    return ScheduleCallbackResponsePayload(task_id=task_id)


routers = [router, scheduler]
