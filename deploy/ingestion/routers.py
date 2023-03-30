from fastapi.openapi.models import APIKey
from krules_fastapi_env import KRulesAPIRouter
from fastapi import Request, Header, Security, HTTPException, Depends
from krules_core.providers import event_router_factory
from starlette.status import HTTP_403_FORBIDDEN

from common.event_types import SUBJECT_PROPERTIES_DATA
from fastapi.security.api_key import APIKeyHeader
import os

router = KRulesAPIRouter(
    prefix="/api/v1",
    tags=["ingestion"],
    responses={404: {"description": "Not found"}},
)

api_key_header = APIKeyHeader(name="api-key", auto_error=False)


async def get_api_key(header: str = Security(api_key_header)):
    if header == os.environ["API_KEY"]:
        return header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


@router.post("/{subscription}/{group}/{entity_id}")
async def ingestion_data(subscription, group, entity_id, data: dict, api_key: APIKey = Depends(get_api_key)):
    # data = await request.json()
    event_router_factory().route(
        subject=f'entity|{subscription}|{group}|{entity_id}',
        event_type=SUBJECT_PROPERTIES_DATA,
        payload={
            "data": data
        }
    )


routers = [router]
