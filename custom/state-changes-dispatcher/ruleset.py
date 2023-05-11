import os
from krules_core import RuleConst as Const
from krules_core.base_functions import *
from krules_core.event_types import *
from krules_core.models import Rule
from state_changes_functions.filters import *
import re


rulesdata = [
    Rule(
        name="wallbox-entity-state-changes-dispatcher",
        filters=[
            IsSubscription(0),
            GroupMatch(re.compile("^urmet\.wallbox\..+")),
        ],
        processing=[
            Route(
                topic="projects/krules-dev-254113/topics/wallbox-chargers-state-changes",
                dispatch_policy=DispatchPolicyConst.DIRECT
            )
        ]
    )
]
