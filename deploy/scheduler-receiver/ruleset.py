from krules_core.base_functions.processing import *
from krules_core.models import Rule


from common.event_types import IngestionEventsV1
from ruleset_functions import SingleScheduleEvent, MultiScheduleEvents


rulesdata: List[Rule] = [
    Rule(
        name="receive-entity-schedule-event",
        subscribe_to=[
            IngestionEventsV1.ENTITY_SCHEDULE,
        ],
        processing=[
            SingleScheduleEvent()
        ]
    ),
    Rule(
        name="receive-group-schedule-event",
        subscribe_to=[
            IngestionEventsV1.GROUP_SCHEDULE,
        ],
        processing=[
            MultiScheduleEvents()
        ]
    )

]
