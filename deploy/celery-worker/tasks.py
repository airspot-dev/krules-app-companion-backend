from celery import Celery
import os
import requests
from google.cloud import secretmanager


client = secretmanager.SecretManagerServiceClient()
celery_broker = os.environ.get("CELERY_BROKER")
if celery_broker is None:
    secret_path = os.environ.get("CELERY_BROKER_SECRET_PATH")
    if secret_path:
        response = client.access_secret_version(name=secret_path)
        celery_broker = response.payload.data.decode('utf-8')
celery_result_backend=os.environ.get("CELERY_RESULTS_BACKEND")
if celery_result_backend is None:
    secret_path = os.environ.get("CELERY_RESULTS_BACKEND_SECRET_PATH")
    if secret_path:
        response = client.access_secret_version(name=secret_path)
        celery_result_backend = response.payload.data.decode('utf-8')

app = Celery('tasks',
             broker=celery_broker,
             result_backend=celery_result_backend
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
