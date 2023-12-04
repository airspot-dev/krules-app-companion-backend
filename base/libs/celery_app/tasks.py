import os

import celery

from common.event_types import SystemEventsV1
from . import app

from krules_core.providers import event_router_factory

class BaseTask(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        event_router_factory().route(
            SystemEventsV1.CALLBACK_FAILED,
            f"tasks|{task_id}",
            {
                "exc": exc,
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "einfo": einfo,
            },
            topic=os.environ["SCHEDULER_ERRORS_TOPIC"]
        )


@app.task(base=BaseTask)
def schedule(subscription, group, entity_id, message):
    print(subscription, group, entity_id, message)


@app.task(base=BaseTask)
def schedule_multi(subscription, group, filter, message):
    print(subscription, group, filter, message)