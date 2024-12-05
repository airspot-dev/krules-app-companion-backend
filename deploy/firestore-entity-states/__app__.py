from krules_fastapi_env import KRulesApp
from contextlib import asynccontextmanager

from krules_pubsub.subscriber import PubSubSubscriber

import logging

logger = logging.getLogger("rich")


@asynccontextmanager
async def lifespan(app: KRulesApp):

    subscriber = await PubSubSubscriber.create(logger)
    subscriber.add_process_function_for_subject(
        ".*",
        PubSubSubscriber.KRulesEventRouterHandler(subscriber.logger)
    )

    yield

    await subscriber.stop()


app = KRulesApp(lifespan=lifespan)
