from krules_core.providers import event_dispatcher_factory, subject_storage_factory
from krules_cloudevents_pubsub.route.dispatcher import CloudEventsDispatcher
from dependency_injector import providers
from krules_env import get_source, RULE_PROC_EVENT
import os
import google.auth
from redis_subjects_storage.storage_impl import SubjectsRedisStorage
from google.cloud import secretmanager
import re
import logging

logger = logging.getLogger()


_, PROJECT = google.auth.default()


def _get_topic_id(subject, event_type):

    if event_type == RULE_PROC_EVENT:
        return os.environ.get("PROCEVENTS_TOPIC", os.environ.get("DEFAULTSINK_TOPIC"))
    else:
        topic_name = os.environ.get("DEFAULTSINK_TOPIC")

    return topic_name


def init():
    event_dispatcher_factory.override(
        providers.Singleton(lambda: CloudEventsDispatcher
            (
                project_id=PROJECT,
                topic_id=_get_topic_id,
                source=get_source(),
            )
        )
    )

    client = secretmanager.SecretManagerServiceClient()
    subjects_redis_url = os.environ.get("SUBJECTS_REDIS_URL")
    if subjects_redis_url is None:
        secret_path = os.environ.get("SUBJECTS_REDIS_URL_SECRET_PATH")
        if secret_path:
            response = client.access_secret_version(name=secret_path)
            subjects_redis_url = response.payload.data.decode('utf-8')
    if subjects_redis_url:
        subjects_redis_prefix = os.environ.get("SUBJECTS_REDIS_PREFIX")
        if subjects_redis_prefix is None:
            if "PROJECT_NAME" in os.environ and "TARGET" in os.environ:
                subjects_redis_prefix = f"{os.environ['PROJECT_NAME']}-{os.environ['TARGET']}->"
            else:
                raise Exception("SUBJECTS_REDIS_PREFIX not configured")
        subject_storage_factory.override(
            providers.Factory(
                lambda name, **kwargs:
                SubjectsRedisStorage(
                    name,
                    subjects_redis_url,
                    key_prefix=subjects_redis_prefix
                )
            )
        )