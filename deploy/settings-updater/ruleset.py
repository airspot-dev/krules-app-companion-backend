from krules_core.base_functions.processing import *
from krules_core.models import Rule


from common.event_types import SystemEventsV1


rulesdata: List[Rule] = [
    Rule(
        name="schema-updater",
        description="""
            Receive schema updates, store on per group subject
        """,
        subscribe_to=[
            SystemEventsV1.SCHEMA_UPDATED,
        ],
        processing=[
            SetSubjectProperties(
                lambda payload: payload
            ),
            StoreSubject()
        ]
    )
]
