import os

from celery import Celery
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
celery_broker = os.environ.get("CELERY_BROKER")
if celery_broker is None:
    secret_path = os.environ.get("CELERY_BROKER_SECRET_PATH")
    if secret_path:
        response = client.access_secret_version(name=secret_path)
        celery_broker = response.payload.data.decode('utf-8')
celery_result_backend = os.environ.get("CELERY_RESULT_BACKEND")
if celery_result_backend is None:
    secret_path = os.environ.get("CELERY_RESULT_BACKEND_SECRET_PATH")
    if secret_path:
        response = client.access_secret_version(name=secret_path)
        celery_result_backend = response.payload.data.decode('utf-8')

app = Celery(
    'cm-scheduler',
    broker=celery_broker,
    result_backend=celery_result_backend,
#    accept_content='pickle'
)
