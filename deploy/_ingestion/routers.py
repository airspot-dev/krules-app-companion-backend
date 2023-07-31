from typing import Optional

import google.oauth2.id_token
import google.auth.transport.requests
from fastapi.openapi.models import APIKey
from krules_fastapi_env import KRulesAPIRouter
from fastapi import Request, Header, Security, HTTPException, Depends
from krules_core.providers import event_router_factory
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from common.event_types import IngestionEventsV1
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import google.auth.exceptions
import os

router = KRulesAPIRouter(
    prefix="/api/v1",
    tags=["ingestion"],
    responses={404: {"description": "Not found"}},
)

GOOGLE_HTTP_REQUEST = google.auth.transport.requests.Request()

api_key_header = APIKeyHeader(name="api-key", auto_error=False)
firestore_token_header = APIKeyHeader(name="Authorization", auto_error=False)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_api_key(header: str = Security(api_key_header)):
    if header == os.environ["API_KEY"]:
        return header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


async def check_firebase_user(header: str = Security(firestore_token_header), api_key_header: str = Security(api_key_header)):
    if api_key_header == os.environ["API_KEY"]:
        return header
    else:
        if not firestore_token_header:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Authorization header missing"
            )
        id_token = header.split(' ').pop()
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, GOOGLE_HTTP_REQUEST, audience=os.environ.get('GOOGLE_CLOUD_PROJECT')
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


@router.delete("/{subscription}/{group}", summary="Delete group")
async def delete_group(subscription, group: str, token: APIKey = Depends(check_firebase_user)):
    event_router_factory().route(
        subject=f'group|{subscription}|{group}',
        event_type=IngestionEventsV1.GROUP_DELETE,
        payload={
            "token": token
        }
    )


@router.delete("/{subscription}/{group}/{entity_id}", summary="Delete entity")
async def delete_entity(subscription, group, entity_id: str, token: APIKey = Depends(check_firebase_user)):
    event_router_factory().route(
        subject=f'entity|{subscription}|{group}|{entity_id}',
        event_type=IngestionEventsV1.ENTITY_DELETE,
        payload={
            "token": token
        }
    )


@router.post("/{subscription}/{group}")
async def ingestion_data(subscription, group, body: GroupUpdatePayload, api_key: APIKey = Depends(get_api_key)):
    # data = await request.json()
    if body.entities_filter is None:
        body.entities_filter = []
    event_router_factory().route(
        subject=f'group|{subscription}|{group}',
        event_type=IngestionEventsV1.GROUP_DATA,
        payload={
            "data": body.data,
            "entities_filter": body.entities_filter,
        }
    )


@router.post("/{subscription}/{group}/{entity_id}")
async def ingestion_data(subscription, group, entity_id, data: dict, api_key: APIKey = Depends(get_api_key)):
    # data = await request.json()
    event_router_factory().route(
        subject=f'entity|{subscription}|{group}|{entity_id}',
        event_type=IngestionEventsV1.ENTITY_DATA,
        payload={
            "data": data
        }
    )


routers = [router]
