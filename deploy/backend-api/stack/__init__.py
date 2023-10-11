import pulumi
import pulumi_gcp as gcp
from pulumi import StackReference, Config
from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.components import DockerImageBuilder
from pulumi_gcp.cloudrunv2.outputs import ServiceTemplateContainerEnvValueSourceSecretKeyRef, \
    ServiceTemplateContainerEnv, ServiceTemplateContainerEnvValueSource

config = Config()

base_stack_ref = StackReference(config.require('base_stack'))

app_name = sane_utils.check_env("app_name")
project_name = sane_utils.check_env("project_name")
target, _ = sane_utils.get_targets_info()
region = sane_utils.get_var_for_target("region")
project_id = sane_utils.get_var_for_target("project_id")
firestore_project_id = sane_utils.get_var_for_target("FIRESTORE_PROJECT_ID", default=project_id)

vpcaccess_connector_project_id = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_PROJECT_ID", default=project_id)
vpcaccess_connector_location = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_LOCATION")
vpcaccess_connector_name = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_NAME")

image = DockerImageBuilder(
    f"{app_name}-image",
    image_name=base_stack_ref.get_output('docker_repository').apply(
        lambda repository:
            f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}"
    ),
).build()

pulumi.export("image", image)

backend_api_service = gcp.cloudrunv2.Service(
    f"{project_name}-{app_name}-{target}",
    ingress="INGRESS_TRAFFIC_ALL",
    project=project_id,
    location=region,
    template=gcp.cloudrunv2.ServiceTemplateArgs(
        containers=[
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=image.repo_digest.apply(
                    lambda digest:
                        base_stack_ref.get_output('docker_repository').apply(
                            lambda repository:
                                f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}@{digest.split('@')[1]}"
                        )
                ),
                envs=[
                    ServiceTemplateContainerEnv(
                        name="PUBLISH_PROCEVENTS_LEVEL",
                        value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_LEVEL", default="0")
                    ),
                    ServiceTemplateContainerEnv(
                        name="PUBLISH_PROCEVENTS_MATCHING",
                        value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_MATCHING", default="*")
                    ),
                    ServiceTemplateContainerEnv(
                        name="PROJECT_NAME",
                        value=project_name
                    ),
                    ServiceTemplateContainerEnv(
                        name="PUBSUB_SINK",
                        value=f'{project_name}-ingestion-{target}',
                    ),
                    ServiceTemplateContainerEnv(
                        name="PUBSUB_PROCEVENTS_SINK",
                        value=f'{project_name}-procevents-{target}',
                    ),
                    ServiceTemplateContainerEnv(
                        name="TARGET",
                        value=target
                    ),
                    ServiceTemplateContainerEnv(
                        name="FIRESTORE_PROJECT_ID",
                        value=firestore_project_id
                    ),
                    ServiceTemplateContainerEnv(
                        name="API_KEY",
                        value_source=ServiceTemplateContainerEnvValueSource(
                            secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRef(
                                secret=f"{project_name}-ingestion_api_key-{target}",
                                version="latest"
                            )
                        ),
                    ),
                    ServiceTemplateContainerEnv(
                        name="CELERY_BROKER",
                        value_source=ServiceTemplateContainerEnvValueSource(
                            secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRef(
                                secret=f"{project_name}-celery_broker-{target}",
                                version="latest"
                            )
                        ),
                    ),
                    ServiceTemplateContainerEnv(
                        name="CELERY_RESULTS_BACKEND",
                        value_source=ServiceTemplateContainerEnvValueSource(
                            secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRef(
                                secret=f"{project_name}-celery_results_backend-{target}",
                                version="latest"
                            )
                        ),
                    )
                ],
            )],
        vpc_access=gcp.cloudrunv2.ServiceTemplateVpcAccessArgs(
            connector=f'projects/{vpcaccess_connector_project_id}/locations/{vpcaccess_connector_location}/connectors/{vpcaccess_connector_name}',
            egress="ALL_TRAFFIC",
        )
    )
)

pulumi.export("backend_api_service", backend_api_service)
