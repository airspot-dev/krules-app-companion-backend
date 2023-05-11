import os

from krules_core.base_functions import *
from krules_core.models import Rule

import google.cloud.logging
client = google.cloud.logging.Client()
logger = client.logger(f"{os.environ['PROJECT_NAME']}-procevents-{os.environ['TARGET']}")


rulesdata: List[Rule] = [
    Rule(
        name="send-procevent-to-gcp-logger",
        processing=[
            Process(lambda payload: payload.pop("_event_info")),
            Process(
                lambda payload: (
                    logger.log_struct(
                        payload,
                        severity=payload["got_errors"] and "ERROR" or "INFO",
                        labels={
                            "krules.dev/app": "procevent-logger-publisher",
                            "krules.dev/project": os.environ["PROJECT_NAME"],
                        }
                    )
                )
            )
        ]
    )
]
