import os
import random
from datetime import timedelta

import celery
import firebase_admin
import pysnooper
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from pydantic import ValidationError
from dateutil.parser import parse

from common.event_types import SystemEventsV1
from common.models.channels import Channel
from common.models.scheduler import SchedulerCallbackPayload, EntityUpdatedCallbackPayload
from . import app

try:
    import krules_env

    krules_env.init()
except:  # avoid circular import
    pass

firebase_admin.initialize_app()

from krules_core.providers import event_router_factory, subject_factory


def _get_db():
    return firestore.Client(project=os.environ["FIRESTORE_PROJECT_ID"], database=os.environ["FIRESTORE_DATABASE"])


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


def _send_callback(task, channels, group, subscription, entity_id, entity_data, message):
    payload = SchedulerCallbackPayload(
        last_updated=entity_data.pop("_last_update"),  # .isoformat(),
        task_id=task.request.id,
        subscription=subscription,
        group=group,
        id=entity_id,
        state=entity_data,
        message=message,
    )

    # print(payload.model_dump_json(indent=4))

    def _exception_handler(ex):
        event_router_factory().route(
            SystemEventsV1.CALLBACK_CHANNEL_SEND_FAILURE,
            f"tasks|{task.request.id}",
            {
                "subscription": subscription,
                "channel": channel,
                "err": str(ex)
            },
            topic=os.environ["USER_ERRORS_TOPIC"]
        )

    if task.request.headers and "replace_id" in task.request.headers:
        def _unset_replace_id(replace_ids):
            if replace_ids is None:
                replace_ids = {}
            replace_id = task.request.headers.get("replace_id")
            if replace_id in replace_ids:
                del replace_ids[replace_id]
            return replace_ids

        entity = subject_factory(f"entity|{payload.subscription}|{payload.group}|{payload.id}")
        entity.set("replace_ids", _unset_replace_id, use_cache=False)

    for channel in channels:
        try:
            ch = Channel(
                **subject_factory(f"channel|{subscription}|{channel}").dict()
            )
            ch.implementation().send(payload, _exception_handler)
        except ValidationError as err:
            event_router_factory().route(
                SystemEventsV1.CALLBACK_CHANNEL_INVALID,
                f"tasks|{task.request.id}",
                {
                    "subscription": subscription,
                    "channel": channel,
                    "err": str(err)
                },
                topic=os.environ["USER_ERRORS_TOPIC"]
            )
            raise


@app.task(base=BaseTask, bind=True)
def schedule(self, subscription, group, entity_id, message, channels):
    db = _get_db()
    doc_ref = db.collection(f"{subscription}/groups/{group}").document(entity_id)
    entity_data = doc_ref.get().to_dict()
    if entity_data is None:
        # TODO: Let the user specify his own error reporting channel
        event_router_factory().route(
            SystemEventsV1.CALLBACK_ENTITY_NOTFOUND,
            f"tasks|{self.request.id}",
            {
                "subscription": subscription,
                "group": group,
                "entity_id": entity_id,
            },
            topic=os.environ["USER_ERRORS_TOPIC"]
        )
    else:
        _send_callback(self, channels, group, subscription, entity_id, entity_data, message)


@app.task(base=BaseTask, bind=True)
def schedule_multi(self, subscription, group, filter, message, channels, task_rnd_delay, fresh_data):
    with pysnooper.snoop(watch='self.request'):
        db = _get_db()
        if filter is not None and len(filter) > 0:
            docs = db.collection(f"{subscription}/groups/{group}").where(filter=FieldFilter(*filter)).stream()
        else:
            docs = db.collection(f"{subscription}/groups/{group}").stream()
        for doc in docs:
            eta = self.request.eta
            if task_rnd_delay and task_rnd_delay > 0:
                eta = parse(self.request.eta) + timedelta(seconds=random.randint(0, task_rnd_delay))
            if fresh_data:
                schedule.apply_async(
                    args=[subscription, group, doc.id, message, channels],
                    eta=eta
                )
            else:
                schedule_multi_fetched.apply_async(
                    args=[channels, group, subscription, doc.id, doc.to_dict(), message],
                    eta=eta
                )


@app.task(base=BaseTask, bind=True)
def schedule_multi_fetched(self, channels, subscription, group, entity_id, entity_data, message):
    _send_callback(self, channels, subscription, group, entity_id, entity_data, message)


@app.task(base=BaseTask, bind=True)
def send_entity_event(self, event, channels):
    try:
        callback = EntityUpdatedCallbackPayload.parse_obj(event)
    except ValidationError as e:
        print(e.json())
        raise
    subscription = callback.subscription
    for channel in channels:
        ch = Channel(
            **subject_factory(f"channel|{subscription}|{channel}").dict()
        )
        ch.implementation().send(callback, lambda ex: print(ex))
