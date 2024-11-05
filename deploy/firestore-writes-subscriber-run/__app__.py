from contextlib import asynccontextmanager

from krules_fastapi_env import KrulesApp
from routers import entities_router, schemas_router, channels_router, triggers_router, settings_router


@asynccontextmanager
async def lifespan(_app: KrulesApp):
    yield

app = KrulesApp(lifespan=lifespan)
routers = [entities_router, schemas_router, channels_router, triggers_router, settings_router]
for router in routers:
    app.include_router(router)
