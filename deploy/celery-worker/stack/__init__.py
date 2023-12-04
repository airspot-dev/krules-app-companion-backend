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

deployment = GkeDeployment(
    app_name,
    gcp_repository=gcp_repository,
    access_secrets=[
        "subjects_redis_url",
        "celery_broker",
        "celery_results_backend",
    ],
    publish_to={
        "procevents": topic_procevents,
    },
    # subscribe_to={
    #     "defaultsink": topic_defaultsink,
    #     "ingestion": topic_ingestion,
    # }

)

