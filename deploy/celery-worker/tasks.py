from celery import Celery
import os
import requests

app = Celery('tasks',
             broker=os.environ["CELERY_BROKER"],
             result_backend=os.environ["CELERY_RESULTS_BACKEND"]
             )

@app.task
def callback(
        subscription: int, group: str, entity: str,
        url: str = None, header: tuple = (None, None), topic: str = None, channels: list = None,
        message: str = None,
        replace_id: str = None,
):
    # TODO: get entity state

    payload = {
        "subscription": subscription,
        "group": group,
        "entity": entity,
        "state": {}
    }

    if message is not None:
        payload["message"] = message

    if url is not None:
        headers = {}
        if header is not None and len(header) == 2 and header[0] is not None:
            headers[header[0]] = header[1]

        return requests.post(url, headers=headers, json=payload)
