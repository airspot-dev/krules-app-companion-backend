from contextlib import asynccontextmanager

from krules_fastapi_env import KRulesApp
from routers import routers


@asynccontextmanager
async def lifespan(_app: KRulesApp):
    yield

app = KRulesApp(lifespan=lifespan)
for router in routers:
    app.include_router(router)
