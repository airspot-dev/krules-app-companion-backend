import pulumi
import pulumi_gcp as gcp
from pulumi import Config
from pulumi_gcp.artifactregistry import Repository
from pulumi_kubernetes.core.v1 import EnvVarArgs

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

topic_ingestion = gcp.pubsub.Topic.get(
    "ingestion",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("ingestion").get("id")
    )
)

topic_scheduler = gcp.pubsub.Topic.get(
    "scheduler",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("scheduler").get("id")
    )
)

deployment = GkeDeployment(
    app_name,
    service_type="ClusterIP",
    gcp_repository=gcp_repository,
    access_secrets=[
        "ingestion_api_key",
    ],
    publish_to={
        "ingestion": topic_ingestion,
        "scheduler": topic_scheduler,
    },
    app_container_kwargs=dict(
        env=[
            EnvVarArgs(
                name="FIRESTORE_PROJECT_ID",
                value=sane_utils.get_firestore_project_id(),
            ),
        ]
    ),
    #use_firestore=True,
)


# TODO: remove it (needed to get subscriptis)
# gcp.projects.IAMMember(
#     "firebase_admin",
#     member=deployment.sa.sa.email.apply(
#         lambda email: f"serviceAccount:{email}"
#     ),
#     project=sane_utils.get_project_id(),
#     role="roles/firebaseauth.admin",
# )


pulumi.export("service", deployment.service)
