import pulumi
from pulumi import Config
from pulumi_gcp.artifactregistry import Repository
from pulumi_gcp.pubsub import Topic

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference
from krules_dev.sane_utils.pulumi.components import GkeDeployment

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
topic_scheduler = Topic.get(
    "scheduler-topic",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("scheduler").get("id")
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

deployment = GkeDeployment(
    app_name,
    gcp_repository=gcp_repository,
    access_secrets=[
        "subjects_redis_url",
        "celery_broker",
        "celery_results_backend",
    ],
    subscribe_to=[
        (
            "scheduler",
            {
                "topic": topic_scheduler.name,
                "ack_deadline_seconds": 20,
            }
        ),
    ],
    publish_to={
        "procevents": topic_procevents,
        "scheduler-errors": topic_scheduler_errors,
    },
)

