from typing import List

from krules_core.base_functions.processing import ProcessingFunction
from krules_core.models import Rule

from __app__ import subscriptions_data, data_lock, update_subscription
from celery_app import tasks
from common.event_types import SystemEventsV1
from common.models.entities import EntityEvent


class ProcessTriggers(ProcessingFunction):

    def execute(self):
        event = EntityEvent(
            type=self.event_type,
            **self.payload
        )
        with data_lock:
            if event.subscription not in subscriptions_data:
                update_subscription(event.subscription)
            subscription = subscriptions_data[event.subscription]
            print(">> processing triggers")
            for trigger_name, trigger in subscription.triggers.items():
                print(">>> ", trigger_name)
                if trigger.applies_to(event):
                    print(">>> OK")
                    tasks.send_entity_event.delay(event.model_dump(), trigger.channels)

        print(event.model_dump_json(indent=2))
        print(str(subscriptions_data))


rulesdata: List[Rule] = [
    Rule(
        name="trigger-processor-receives-entity-data",
        subscribe_to=[
            SystemEventsV1.ENTITY_CREATED,
            SystemEventsV1.ENTITY_UPDATED,
            SystemEventsV1.ENTITY_DELETED,
        ],
        processing=[
            ProcessTriggers()
        ]
    ),
]
