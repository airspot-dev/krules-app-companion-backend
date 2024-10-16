from contextlib import asynccontextmanager

from krules_fastapi_env import KrulesApp
from routers import routers


@asynccontextmanager
async def lifespan(_app: KrulesApp):
    yield

app = KrulesApp(lifespan=lifespan)
for router in routers:
    app.include_router(router)
