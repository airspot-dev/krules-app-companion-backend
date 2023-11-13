from krules_core.base_functions.processing import Route
from krules_core.models import Rule
from krules_core.route.router import DispatchPolicyConst

rulesdata = [
    # Rule(
    #     name="cloudevent-dispatcher",
    #     #subscribe_to=["*"],
    #     description=
    #     """
    #         Route cloud events to ingestion topic
    #     """,
    #     processing=[
    #         Route(
    #             dispatch_policy=DispatchPolicyConst.DIRECT
    #         )
    #     ]
    # ),
]
