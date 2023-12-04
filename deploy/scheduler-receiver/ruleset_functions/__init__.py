from datetime import datetime, timedelta
from dateutil.parser import parse

from krules_core.base_functions.processing import ProcessingFunction

from celery_app import app, tasks


def _extract_eta(data):
    now = data.pop("now")
    eta = datetime.now()
    seconds = data.pop("seconds")
    when = data.pop("when")
    if not now:
        if seconds:
            eta = eta + timedelta(seconds=seconds)
        elif when:
            eta = parse(when)

    return eta


class SingleScheduleEvent(ProcessingFunction):

    def execute(self):
        data = self.payload.get("data", {})
        eta = _extract_eta(data)

        task_id = data.pop("task_id")
        replace_id = data.pop("replace_id")
        if replace_id is not None:
            app.control.revoke(
                replace_id
            )

        tasks.schedule.apply_async(
            eta=eta,
            task_id=task_id,
            kwargs=dict(
                subscription=data.get("subscription"),
                group=data.get("group"),
                entity_id=data.get("entity_id"),
                message=data.get("message")
            )
        )


class MultiScheduleEvents(ProcessingFunction):

    def execute(self):
        data = self.payload.get("data", {})
        eta = _extract_eta(data)
        task_id = data.pop("task_id")

        tasks.schedule_multi.apply_async(
            eta=eta,
            task_id=task_id,
            kwargs=dict(
                subscription=data.get("subscription"),
                group=data.get("group"),
                filter=data.get("filter"),
                message=data.get("message")
            )
        )
