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

topic_procevents = gcp.pubsub.Topic.get(
    "procevents",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("procevents").get("id")
    )
)


access_secrets = []
envs = []

subjects_redis_url = sane_utils.get_var_for_target("subjects_redis_url", default=None)
if subjects_redis_url is not None:
    envs.append(
        EnvVarArgs(
            name="SUBJECTS_REDIS_URL",
            value=subjects_redis_url,
        ),
    )
else:
    access_secrets.append("subjects_redis_url")

deployment = GkeDeployment(
    app_name,
    gcp_repository=gcp_repository,
    access_secrets=access_secrets,
    app_container_kwargs=dict(
        env=envs
    ),
    subscribe_to=[
        (
            "ingestion",
            {
                "topic": topic_ingestion.name,
                #"enable_exactly_once_delivery": True,
                "ack_deadline_seconds": 20,
            }
        ),
    ],
    publish_to={
        "ingestion": topic_ingestion,
        "procevents": topic_procevents,
    },
    use_firestore=True,
)
pulumi.export("deployment", deployment)



# deployment = kubernetes.apps.v1.Deployment(
#     "deployment",
#     metadata=kubernetes.meta.v1.ObjectMetaArgs(
#         name=app_name,
#         labels={
#             "krules.dev/app": app_name,
#         },
#     ),
#     spec=kubernetes.apps.v1.DeploymentSpecArgs(
#         selector=kubernetes.meta.v1.LabelSelectorArgs(
#             match_labels={
#                 "krules.dev/app": app_name,
#             },
#         ),
#         template=kubernetes.core.v1.PodTemplateSpecArgs(
#             metadata=kubernetes.meta.v1.ObjectMetaArgs(
#                 labels={
#                     "krules.dev/app": app_name,
#                 },
#             ),
#             spec=kubernetes.core.v1.PodSpecArgs(
#                 containers=[
#                     kubernetes.core.v1.ContainerArgs(
#                         image=image.repo_digest,
#                         name=app_name,
#                         env=[
#                             # kubernetes.core.v1.EnvVarArgs(
#                             #     name="PUBLISH_PROCEVENTS_LEVEL",
#                             #     value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_LEVEL", default="0")
#                             # ),
#                             # kubernetes.core.v1.EnvVarArgs(
#                             #     name="PUBLISH_PROCEVENTS_MATCHING",
#                             #     value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_MATCHING", default="*")
#                             # ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="PROJECT_NAME",
#                                 value=project_name
#                             ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="TARGET",
#                                 value=target
#                             ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="APPLICATION_PROJECT_ID",
#                                 value=project_id
#                             ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="FIRESTORE_PROJECT_ID",
#                                 value=firestore_project_id
#                             ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="FIRESTORE_DATABASE",
#                                 value=firestore_db_name
#                             ),
#                         ],
#                         # volume_mounts=[
#                         #     kubernetes.core.v1.VolumeMountArgs(
#                         #         mount_path="/var/secrets/firebase",
#                         #         name="firebase-auth"
#                         #     )
#                         # ]
#                     ),
#                     kubernetes.core.v1.ContainerArgs(
#                         image=sane_utils.check_env("PULL_SUBSCRIBER_IMAGE"),
#                         name="pull-subscriber",
#                         env=[
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="SUBSCRIPTION",
#                                 value=pull_subscription.name
#                             ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="PROJECT",
#                                 value=project_id
#                             ),
#                             kubernetes.core.v1.EnvVarArgs(
#                                 name="CE_SINK",
#                                 value="http://localhost:8080"
#                             ),
#                             # kubernetes.core.v1.EnvVarArgs(
#                             #     name="DEBUG",
#                             #     value="1"
#                             # ),
#                         ]
#                     )
#                 ],
#                 # volumes=[
#                 #     kubernetes.core.v1.VolumeArgs(
#                 #         name="firebase-auth",
#                 #         secret=kubernetes.core.v1.SecretVolumeSourceArgs(
#                 #             secret_name="firebase-auth",
#                 #             # items=[
#                 #             #     kubernetes.core.v1.KeyToPathArgs(
#                 #             #         path="firebase-auth",
#                 #             #         key="firebase-auth"
#                 #             #     )
#                 #             # ]
#                 #         )
#                 #     )
#                 # ]
#             ),
#         ),
#     ),
# )
#
# service = kubernetes.core.v1.Service(
#     "service",
#     metadata=kubernetes.meta.v1.ObjectMetaArgs(
#         name=app_name,
#         labels={
#             "krules.dev/app": app_name,
#         },
#     ),
#     spec=kubernetes.core.v1.ServiceSpecArgs(
#         selector={
#             "krules.dev/app": app_name,
#         },
#         ports=[
#             kubernetes.core.v1.ServicePortArgs(
#                 port=80,
#                 target_port=8080
#             )
#         ]
#     )
# )


