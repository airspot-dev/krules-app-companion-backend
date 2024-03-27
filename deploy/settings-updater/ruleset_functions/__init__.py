from typing import List, Dict

from krules_core.base_functions.processing import ProcessingFunction
from krules_core.providers import subject_factory

from common.event_types import SystemEventsV1
from common.models.subscriptions import Trigger


class UpdateSubscriptionTriggers(ProcessingFunction):

    def execute(self, *args, **kwargs):
        from pprint import pprint
        pprint(self.payload)

        def _update_triggers(value: Dict[str, Trigger]):
            if value is None:
                value = {}
            if self.event_type in [SystemEventsV1.TRIGGER_CREATED, SystemEventsV1.TRIGGER_UPDATED] and self.payload.get('running'):
                value[self.payload.get('id')] = Trigger(**self.payload).dict()
            elif self.event_type == SystemEventsV1.TRIGGER_DELETED or self.payload.get('running') is False:
                pprint(value)
                try:
                    del value[self.payload.get('id')]
                except KeyError:
                    pass
            pprint(value)
            return value

        subject = subject_factory(f"subscription|{self.payload.get('_event_info').get('subscription')}")
        subject.set("triggers", _update_triggers, muted=True)
