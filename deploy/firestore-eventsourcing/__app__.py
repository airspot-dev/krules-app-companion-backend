from krules_fastapi_env import KrulesApp
from contextlib import asynccontextmanager

from krules_pubsub.subscriber import PubSubSubscriber

import logging

logger = logging.getLogger("rich")


@asynccontextmanager
async def lifespan(app: KrulesApp):

    subscriber = await PubSubSubscriber.create(logger)
    subscriber.add_process_function_for_subject(
        ".*",
        PubSubSubscriber.KRulesEventRouterHandler(subscriber.logger)
    )

    yield

    await subscriber.stop()


app = KrulesApp(lifespan=lifespan)
