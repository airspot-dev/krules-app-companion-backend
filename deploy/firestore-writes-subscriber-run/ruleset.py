#from pprint import pprint
import json

from krules_core.base_functions.processing import *
from krules_core.models import Rule

rulesdata: List[Rule] = [
    Rule(
        name="print",
        subscribe_to=[
            "print"
        ],
        processing=[
            Process(
                lambda payload: (
                    print(json.dumps(payload))
                )
            )
        ]
    )
]
