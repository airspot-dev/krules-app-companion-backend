import firebase_admin
import google.oauth2.id_token
import google.auth.transport.requests
from fastapi.openapi.models import APIKey
from krules_fastapi_env import KRulesAPIRouter
from fastapi import Security, HTTPException, Depends
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import google.auth.exceptions
import os
from firebase_admin import auth


firebase_admin.initialize_app()

router = KRulesAPIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


GOOGLE_HTTP_REQUEST = google.auth.transport.requests.Request()

firestore_token_header = APIKeyHeader(name="Authorization", auto_error=False)


class ActiveSubscriptionPayload(BaseModel):
    active_subscription: int


async def check_firebase_user(header: str = Security(firestore_token_header)):

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


@router.get("/subscriptions", summary="Get user subscriptions")
async def get_user_subscriptions(token: APIKey = Depends(check_firebase_user)):
    if token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate authorization token"
        )
    user_data = dict(token)
    print(">>>>>>>>>>>>> user_data: ", str(user_data))
    return {
        "active_subscription": user_data.get("active_subscription", user_data["subscriptions"][0]),
        "subscriptions": user_data["subscriptions"]
    }


@router.post("/subscriptions/activate", summary="Set active subscription")
async def activate_subscription(payload: ActiveSubscriptionPayload, token: APIKey = Depends(check_firebase_user)):

    if token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate authorization token"
        )

    user_data = dict(token)
    user = auth.get_user(user_data["user_id"])
    user_claims = user.custom_claims.copy()
    if payload.active_subscription not in user_claims["subscriptions"]:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"{payload.active_subscription} is not one of the user subscriptions"
        )
    user_claims["active_subscription"] = payload.active_subscription
    auth.update_user(user_data["user_id"], custom_claims=user_claims)


routers = [router]
