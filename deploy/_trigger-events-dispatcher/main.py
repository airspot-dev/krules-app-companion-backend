from fastapi import FastAPI
import logging
import fnmatch
import re
import redis


logger = logging.getLogger(__name__)


def _get_raw_triggers():
    return {
        "*": [
            {

            }
        ],
        "arpa.*": [
            {

            }
        ],
        "wallbox.chargers": [
            {

            }
        ]
    }


def get_triggers():

    triggers = []

    for path, funcs in _get_raw_triggers().items():
        triggers.append(
            (
                re.compile(fnmatch.translate(path)),
                funcs
            )
        )
    return triggers


def exec_triggers_function(event, triggers):

    for t in triggers:
        if event["event"] == t["event"]:
            if event["event"] == "onEntityUpdated" and len(t["entityFields"]) and t["entityFields"] not in event.get(
                    "changed_properties"):
                return
            for channel in t["channels"]:
                send(event, channel)


def send(event, channel):
    pass


app = FastAPI()


@app.on_event("startup")
def on_startup():
    app.state.triggers = get_triggers()


@app.post("/")
def post(data: dict):
    for trigger in app.state.triggers:
        regex, funcs = trigger
        if regex.match(data["group"]):
            exec_triggers_function(data, funcs)
