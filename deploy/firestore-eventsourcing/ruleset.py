from krules_core.base_functions.processing import *
from krules_core.models import Rule


from common.event_types import SystemEventsV1

from ruleset_functions import GetExpireDateFromTTL, EventsourceStore

rulesdata: List[Rule] = [
    Rule(
        name="firestore-eventsourcing-write-updates",
        description="""
            Receive entities updates then writes them into the group's eventsourcing collection
        """,
        subscribe_to=[
            SystemEventsV1.ENTITY_CREATED,
            SystemEventsV1.ENTITY_UPDATED,
        ],
        processing=[
            GetExpireDateFromTTL(payload_dest="_expire_date"),
            EventsourceStore(
                expire_date=lambda payload: payload.get("_expire_date")
            )
        ]
    )
]
