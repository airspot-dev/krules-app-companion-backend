import os
import threading
import time
from contextlib import asynccontextmanager
from typing import Dict

from krules_core.providers import subject_factory
from krules_fastapi_env import KrulesApp

from common.models.subscriptions import Subscription

from krules_pubsub.subscriber import PubSubSubscriber

import logging

logger = logging.getLogger("rich")

data_lock = threading.RLock()

subscriptions_data: Dict[str, Subscription] = {}

# Cache to store Subject instances to avoid redis connections multiplication
subject_cache = {}

def update_subscription(subscription: str):
    try:
        # Reuse existing Subject if available
        if subscription in subject_cache:
            subject = subject_cache[subscription]
        else:
            subject = subject_factory(f"subscription|{subscription}", use_cache_default=False)
            subject_cache[subscription] = subject

        subscriptions_data[subscription] = Subscription(
            **subject.dict()
        )
    except Exception as e:
        print(f">>> ERROR UPDATING SUBSCRIPTION DATA ({subscription}): {e}")


running = True


def _update_subscriptions_data():
    while running:
        with data_lock:
            subscriptions = subscriptions_data.keys()
            for subscription in subscriptions:
                print(">>> REFRESHING ", subscription)
                update_subscription(subscription)
        time.sleep(int(os.environ.get("REFRESH_INTERVAL", 10)))


@asynccontextmanager
async def lifespan(app: KrulesApp):
    global running
    thread = threading.Thread(target=_update_subscriptions_data)
    thread.start()
    subscriber = await PubSubSubscriber.create(logger)
    subscriber.add_process_function_for_subject(
        ".*",
        PubSubSubscriber.KRulesEventRouterHandler(subscriber.logger)
    )
    yield
    await subscriber.stop()
    running = False
    thread.join()


def get_subscriptions_data():
    with data_lock:
        return subscriptions_data


app = KrulesApp(lifespan=lifespan)
