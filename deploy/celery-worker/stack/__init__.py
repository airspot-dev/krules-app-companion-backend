import pulumi
from pulumi import Config
from pulumi_gcp.artifactregistry import Repository
from pulumi_gcp.pubsub import Topic
from pulumi_kubernetes.core.v1 import EnvVarArgs

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference
from krules_dev.sane_utils.pulumi.components import GkeDeployment
from krules_dev.sane_utils.pulumi.components.gke_statefulset import GkeStatefulSet

config = Config()

app_name = sane_utils.check_env("app_name")

base_stack_ref = get_stack_reference("base")

gcp_repository = Repository.get(
    "gcp_repository",
    base_stack_ref.get_output(
        "docker-repository"
    ).apply(
        lambda repository: repository.get("id")
    )
)

topic_procevents = Topic.get(
    "procevents",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("procevents").get("id")
    )
)
topic_scheduler_errors = Topic.get(
    "scheduler-errors",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("scheduler-errors").get("id")
    )
)
topic_user_errors = Topic.get(
    "user-errors",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("user-errors").get("id")
    )
)
deployment = GkeStatefulSet(
    app_name,
    gcp_repository=gcp_repository,
    access_secrets=[
        "subjects_redis_url",
        "celery_broker",
        "celery_result_backend",
    ],
    publish_to={
        "procevents": topic_procevents,
        "scheduler-errors": topic_scheduler_errors,
        "user-errors": topic_user_errors,
    },
    use_firestore=True,
    # app_container_pvc_mounts={
    #     "celery-data": {
    #         "storage": "1Gi",
    #         "mount_path": "/var/lib/celery"
    #     }
    # },
    # app_container_kwargs={
    #     "env": [
    #         EnvVarArgs(
    #             name="CELERY_STATE_DB",
    #             value="/var/lib/celery/state.db",
    #         )
    #     ]
    # }
)


