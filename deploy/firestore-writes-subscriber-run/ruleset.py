from pprint import pprint

from krules_core.base_functions.processing import *
from krules_core.models import Rule

rulesdata: List[Rule] = [
    Rule(
        name="pprint",
        subscribe_to=[
            "pprint"
        ],
        processing=[
            Process(
                lambda payload: (
                    pprint(payload)
                )
            )
        ]
    )
]
