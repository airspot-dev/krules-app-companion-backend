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


# firestore_project_id = sane_utils.get_var_for_target("FIRESTORE_PROJECT_ID", default=project_id)
#
# vpcaccess_connector_project_id = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_PROJECT_ID",
#                                                                default=sane_utils.get_project_id())
# vpcaccess_connector_location = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_LOCATION")
# vpcaccess_connector_name = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_NAME")
# vpc_access = gcp.cloudrunv2.ServiceTemplateVpcAccessArgs(
#     connector=f'projects/{vpcaccess_connector_project_id}/locations/{vpcaccess_connector_location}/connectors/{vpcaccess_connector_name}',
#     egress="ALL_TRAFFIC",
# )


# service = CloudRun(
#     f"run_{app_name}",
#     gcp_repository=gcp_repository,
#     service_kwargs=dict(
#         ingress="INGRESS_TRAFFIC_ALL",
#     ),
#     require_authentication=False,
#     service_template_kwargs={
#         "vpc_access": vpc_access,
#     },
#     access_secrets=[
#         "ingestion_api_key",
#         "celery_broker",
#         "celery_results_backend",
#         "subjects_redis_url",
#     ],
#     publish_to={
#         "ingestion": topic_ingestion,
#     },
#     app_container_kwargs=dict(
#         envs=[
#             ServiceTemplateContainerEnvArgs(
#                 name="FIRESTORE_PROJECT_ID",
#                 value=sane_utils.get_firestore_project_id(),
#             ),
#         ]
#     )
# )
#
deployment = GkeDeployment(
    app_name,
    service_type="ClusterIP",
    gcp_repository=gcp_repository,
    access_secrets=[
        "ingestion_api_key",
        "celery_broker",
        "celery_results_backend",
        "subjects_redis_url",
    ],
    publish_to={
        "ingestion": topic_ingestion,
    },
    app_container_kwargs=dict(
        env=[
            EnvVarArgs(
                name="FIRESTORE_PROJECT_ID",
                value=sane_utils.get_firestore_project_id(),
            ),
        ]
    )
)

# image = DockerImageBuilder(
#     f"{app_name}-image",
#     image_name=base_stack_ref.get_output('docker_repository').apply(
#         lambda repository:
#             f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}"
#     ),
# ).build()
#
# pulumi.export("image", image)
#
# backend_api_service = gcp.cloudrunv2.Service(
#     f"{project_name}-{app_name}-{target}",
#     ingress="INGRESS_TRAFFIC_ALL",
#     project=project_id,
#     location=region,
#     template=gcp.cloudrunv2.ServiceTemplateArgs(
#         containers=[
#             gcp.cloudrunv2.ServiceTemplateContainerArgs(
#                 image=image.repo_digest.apply(
#                     lambda digest:
#                         base_stack_ref.get_output('docker_repository').apply(
#                             lambda repository:
#                                 f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}@{digest.split('@')[1]}"
#                         )
#                 ),
#                 envs=[
#                     ServiceTemplateContainerEnvArgs(
#                         name="PUBLISH_PROCEVENTS_LEVEL",
#                         value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_LEVEL", default="0")
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="PUBLISH_PROCEVENTS_MATCHING",
#                         value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_MATCHING", default="*")
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="PROJECT_NAME",
#                         value=project_name
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="PUBSUB_SINK",
#                         value=f'{project_name}-ingestion-{target}',
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="PUBSUB_PROCEVENTS_SINK",
#                         value=f'{project_name}-procevents-{target}',
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="TARGET",
#                         value=target
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="FIRESTORE_PROJECT_ID",
#                         value=firestore_project_id
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="API_KEY",
#                         value_source=ServiceTemplateContainerEnvValueSourceArgs(
#                             secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
#                                 secret=f"{project_name}-ingestion_api_key-{target}",
#                                 version="latest"
#                             )
#                         ),
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="CELERY_BROKER",
#                         value_source=ServiceTemplateContainerEnvValueSourceArgs(
#                             secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
#                                 secret=f"{project_name}-celery_broker-{target}",
#                                 version="latest"
#                             )
#                         ),
#                     ),
#                     ServiceTemplateContainerEnvArgs(
#                         name="CELERY_RESULTS_BACKEND",
#                         value_source=ServiceTemplateContainerEnvValueSourceArgs(
#                             secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
#                                 secret=f"{project_name}-celery_results_backend-{target}",
#                                 version="latest"
#                             )
#                         ),
#                     )
#                 ],
#             )],
#     )
# )
#
# pulumi.export("backend_api_service", backend_api_service)
