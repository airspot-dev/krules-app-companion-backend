from krules_core.base_functions import *
from krules_core.models import Rule


rulesdata = [
    Rule(
        name="cloudevent-dispatcher",
        description=
        """
            Route cloud events to ingestion topic
        """,
        processing=[
            Route(
                dispatch_policy=DispatchPolicyConst.DIRECT
            )
        ]
    ),
]
