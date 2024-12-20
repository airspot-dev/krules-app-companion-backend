import pulumi
import pulumi_gcp as gcp
from pulumi import Config
from pulumi_kubernetes.core.v1 import EnvVarArgs

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference
from krules_dev.sane_utils.pulumi.components import GkeDeployment

# Initialize a config object
config = Config()

# Get the name of the "parent" stack that we will reference.
app_name = sane_utils.check_env("app_name")

base_stack_ref = get_stack_reference("base")

gcp_repository = gcp.artifactregistry.Repository.get(
    "gcp_repository",
    base_stack_ref.require_output("docker-repository.id")
)

topic_firestore_updates = gcp.pubsub.Topic.get(
    "firestore-updates",
    base_stack_ref.require_output("topics.firestore-updates.id")
)


topic_procevents = gcp.pubsub.Topic.get(
    "procevents",
    base_stack_ref.require_output("topics.procevents.id")
)


deployment = GkeDeployment(
    app_name,
    gcp_repository=gcp_repository,
    access_secrets=[
        "subjects_redis_url",
    ],
    subscribe_to=[
        (
            "firestore-updates",
            {
                "topic": topic_firestore_updates.name,
                "ack_deadline_seconds": 20,
            }
        ),
    ],
    publish_to={
        "procevents": topic_procevents,
    },
    use_firestore=True,
)



