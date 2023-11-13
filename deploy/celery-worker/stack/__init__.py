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

pulumi.export("deployment", deployment.deployment)
pulumi.export("gsa", deployment.sa)

# image = SaneDockerImage(
#     app_name,
#     gcp_repository=base_outputs.get("docker-repository")
# )
#
# pulumi.export("image", image.image)

# deployment = kubernetes.apps.v1.Deployment("deployment",
#     metadata=kubernetes.meta.v1.ObjectMetaArgs(
#         name=app_name,
#         labels={
#             "krules.dev/app": app_name,
#             "krules.dev/type": "ruleset"
#         },
#     ),
#     spec=kubernetes.apps.v1.DeploymentSpecArgs(
#         replicas=int(sane_utils.get_var_for_target("celery_worker_replicas", default="1")),
#         selector=kubernetes.meta.v1.LabelSelectorArgs(
#             match_labels={
#                 "krules.dev/app": app_name,
#             },
#         ),
#         template=kubernetes.core.v1.PodTemplateSpecArgs(
#             metadata=kubernetes.meta.v1.ObjectMetaArgs(
#                 labels={
#                     "krules.dev/app": app_name,
#                     "krules.dev/type": "ruleset"
#                 },
#             ),
#             spec=kubernetes.core.v1.PodSpecArgs(
#                 containers=[
#                     kubernetes.core.v1.ContainerArgs(
#                         image=image.image.repo_digest,
#                         name=app_name,
#                         env=[],  # TODO
#                         env_from=[
#                             kubernetes.core.v1.EnvFromSourceArgs(
#                                 secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
#                                     name=base_stack_ref.get_output("celery_config_secret").apply(
#                                         lambda secret: secret
#                                     )
#                                 )
#                             )
#                         ]
#                     )
#                 ],
#             ),
#         ),
#     ),
# )
#
# pulumi.export("celery-worker-deployment", deployment)
