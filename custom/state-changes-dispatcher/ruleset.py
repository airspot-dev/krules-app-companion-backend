import os
from krules_core import RuleConst as Const
from krules_core.base_functions import *
from krules_core.event_types import *
from krules_core.models import Rule
from state_changes_functions.filters import *
import re
import json


class JsonDecode(ProcessingFunction):

    def execute(self, properties):

        for prop in properties:
            if prop in self.payload["value"]:
                self.payload["value"][prop] = json.loads(self.payload["value"][prop])
            if prop in self.payload["old_value"]:
                self.payload["old_value"][prop] = json.loads(self.payload["old_value"][prop])



rulesdata = [
    Rule(
        name="wallbox-entity-state-changes-dispatcher",
        filters=[
            IsSubscription(0),
            # GroupMatch(re.compile("^urmet\.wallbox\..+")),
            Filter(lambda payload: payload["group"] == "wallbox.chargers")
        ],
        processing=[
            JsonDecode(properties=["ocpp_received", "ocpp_sent"]),
            Route(
                topic="projects/krules-dev-254113/topics/wallbox-chargers-state-changes",
                dispatch_policy=DispatchPolicyConst.DIRECT,
                payload=lambda payload: payload
            )
        ]
    )
]
