from datetime import datetime, timedelta

import pysnooper
from dateutil.parser import parse

from krules_core.base_functions.processing import ProcessingFunction
from krules_core.providers import subject_factory

from celery_app import app, tasks
from common.models.scheduler import ScheduleCallbackSingleRequest, ScheduleCallbackMultiRequest


# def _extract_eta(data):
#     now = data.pop("now")
#     eta = datetime.now()
#     seconds = data.pop("seconds")
#     when = data.pop("when")
#     if not now:
#         if seconds:
#             eta = eta + timedelta(seconds=seconds)
#         elif when:
#             eta = parse(when)
#
#     return eta


class SingleScheduleEvent(ProcessingFunction):

    def execute(self):
        data = ScheduleCallbackSingleRequest(
            **self.payload.get("data", {})
        )

        subject_match = self.payload.get("subject_match")

        subscription = subject_match.get("subscription")
        group = subject_match.get("group")
        entity_id = subject_match.get("entity_id")

        task_id = self.payload.pop("task_id")

        task_data = data.get_task(
            task_id=task_id,
            subscription=subscription,
            group=group,
            entity_id=entity_id
        )

        headers = {}

        if task_data.replace_id is not None:

            headers["replace_id"] = task_data.replace_id

            def _set_replace_id(replace_ids):

                if replace_ids is None:
                    replace_ids = {}
                if task_data.replace_id in replace_ids:
                    app.control.revoke(
                        replace_ids[task_data.replace_id]
                    )
                replace_ids[task_data.replace_id] = task_id

                return replace_ids

            self.subject.set("replace_ids", _set_replace_id, use_cache=False)

        tasks.schedule.apply_async(
            eta=task_data.eta,
            task_id=task_data.task_id,
            headers=headers,
            kwargs=dict(
                subscription=task_data.subscription,
                group=task_data.group,
                entity_id=task_data.entity_id,
                message=task_data.message,
                channels=task_data.channels,
            )
        )


class MultiScheduleEvents(ProcessingFunction):

    def execute(self):
        with pysnooper.snoop(watch_explode=('self',), max_variable_length=None):
            data = ScheduleCallbackMultiRequest(
                **self.payload.get("data", {})
            )

            subject_match = self.payload.get("subject_match")

            subscription = subject_match.get("subscription")
            group = subject_match.get("group")

            task_id = self.payload.pop("task_id")

            task_data = data.get_task(
                task_id=task_id,
                subscription=subscription,
                group=group,
            )

            tasks.schedule_multi.apply_async(
                    eta=task_data.eta,
                    task_id=task_data.task_id,
                    kwargs=dict(
                        subscription=task_data.subscription,
                        group=task_data.group,
                        filter=task_data.filter,
                        message=task_data.message,
                        channels=task_data.channels,
                        task_rnd_delay=task_data.task_rnd_delay,
                        fresh_data=task_data.fresh_data,
                    )
                )
