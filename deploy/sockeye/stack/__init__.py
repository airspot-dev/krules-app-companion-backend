import pulumi
from pulumi import Config
from pulumi_gcp.artifactregistry import Repository
from pulumi_gcp.pubsub import Topic
from pulumi_kubernetes.core.v1 import ServiceSpecType

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

topic_defaultsink = Topic.get(
    "defaultsink",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("defaultsink").get("id")
    )
)

deployment = GkeDeployment(
    app_name,
    service_type=ServiceSpecType.CLUSTER_IP,
    gcp_repository=gcp_repository,
    subscribe_to=[
        (
            "defaultsink",
            {
                "topic": topic_defaultsink.name,
                "enable_exactly_once_delivery": True,
                "ack_deadline_seconds": 20,
            }
        ),
        (
            "procevents",
            {
                "topic": topic_procevents.name,
                "enable_exactly_once_delivery": True,
                "ack_deadline_seconds": 20,
            }
        )
    ]
)

pulumi.export("deployment", deployment.deployment)
pulumi.export("gsa", deployment.sa)

