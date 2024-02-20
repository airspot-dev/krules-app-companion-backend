import threading
import time
from contextlib import asynccontextmanager
from typing import Dict

from krules_core.providers import subject_factory
from krules_fastapi_env import KrulesApp

from common.models.subscriptions import Subscription

data_lock = threading.RLock()

subscriptions_data: Dict[str, Subscription] = {}


def update_subscription(subscription: str):
    try:
        subscriptions_data[subscription] = Subscription(
            **subject_factory(f"subscription|{subscription}").dict()
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
        time.sleep(10)


@asynccontextmanager
async def lifespan(app: KrulesApp):
    global running
    thread = threading.Thread(target=_update_subscriptions_data)
    thread.start()
    yield
    running = False
    thread.join()


def get_subscriptions_data():
    with data_lock:
        return subscriptions_data


app = KrulesApp(lifespan=lifespan)
