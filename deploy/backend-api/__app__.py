from contextlib import asynccontextmanager

from krules_fastapi_env import KrulesApp
from routers import routers
from middlewares import middlewares


@asynccontextmanager
async def lifespan(_app: KrulesApp):
    yield

app = KrulesApp(lifespan=lifespan)
for router in routers:
    app.include_router(router)

for cls, kwargs in middlewares:
    app.add_middleware(cls, **kwargs)