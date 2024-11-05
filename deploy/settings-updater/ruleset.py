from pprint import pprint

from krules_core.base_functions.processing import *
from krules_core.models import Rule

from ruleset_functions import UpdateSubscriptionTriggers

from common.event_types import SystemEventsV1


rulesdata: List[Rule] = [
    Rule(
        name="schema-updater",
        description="""
            Receive schema updates, store on per group subject
        """,
        subscribe_to=[
            SystemEventsV1.SCHEMA_CREATED,
            SystemEventsV1.SCHEMA_UPDATED,
        ],
        processing=[
            Process(
                lambda payload: payload.pop("_event_info")
            ),
            SetSubjectProperties(
                lambda payload: payload
            ),
            StoreSubject()
        ]
    ),
    Rule(
        name="schema-cleanup",
        description="""
            Receive schema delete events, delete subject
        """,
        subscribe_to=[
            SystemEventsV1.SCHEMA_DELETED,
        ],
        processing=[
            FlushSubject()
        ]
    ),
    Rule(
        name="channel-updater",
        description="""
            Receive channel updates, store on subject
        """,
        subscribe_to=[
            SystemEventsV1.CHANNEL_CREATED,
            SystemEventsV1.CHANNEL_UPDATED,
        ],
        processing=[
            Process(
                lambda payload: payload.pop("_event_info")
            ),
            SetSubjectProperties(
                lambda payload: payload
            ),
            StoreSubject()
        ]
    ),
    Rule(
        name="channel-cleanup",
        description="""
            Receive channel delete event, delete subject
        """,
        subscribe_to=[
            SystemEventsV1.CHANNEL_DELETED,
        ],
        processing=[
            FlushSubject()
        ]
    ),
    Rule(
        name="trigger-updater",
        description="""
            Triggers are stored at subsription level
        """,
        subscribe_to=[
            SystemEventsV1.TRIGGER_CREATED,
            SystemEventsV1.TRIGGER_UPDATED,
            SystemEventsV1.TRIGGER_DELETED,
        ],
        processing=[
            UpdateSubscriptionTriggers(),
            StoreSubject()
        ]
    ),
]
