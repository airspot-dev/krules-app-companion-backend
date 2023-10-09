import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as kubernetes
from pulumi import Config, StackReference

from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.components import DockerImageBuilder

# Initialize a config object
config = Config()

# Get the name of the "parent" stack that we will reference.
base_stack_ref = StackReference(config.require('base_stack'))

app_name = sane_utils.check_env("app_name")
target, _ = sane_utils.get_targets_info()
project_name = sane_utils.check_env("project_name")
project_id = sane_utils.get_var_for_target('PROJECT_ID', target, True)
cluster_project_id = sane_utils.get_var_for_target('CLUSTER_PROJECT_ID', target, True)
namespace = sane_utils.get_var_for_target("NAMESPACE", target, default=f"{project_name}-{target}")
cluster_region = sane_utils.get_var_for_target(
    "CLUSTER_REGION", target, default=sane_utils.get_var_for_target("REGION")
)

image = DockerImageBuilder(
    f"{app_name}-image",
    image_name=base_stack_ref.get_output('docker_repository').apply(
        lambda repository: f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}"
    ),
).build()

pulumi.export("image", image)


kubernetes.apps.v1.Deployment(
    "deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=app_name,
        labels={
            "krules.dev/app": app_name,
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "krules.dev/app": app_name,
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "krules.dev/app": app_name,
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        image=image.repo_digest,
                        name=app_name,
                        env=[
                            # kubernetes.core.v1.EnvVarArgs(
                            #     name="PUBLISH_PROCEVENTS_LEVEL",
                            #     value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_LEVEL", default="0")
                            # ),
                            # kubernetes.core.v1.EnvVarArgs(
                            #     name="PUBLISH_PROCEVENTS_MATCHING",
                            #     value=sane_utils.get_var_for_target("PUBLISH_PROCEVENTS_MATCHING", default="*")
                            # ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="PUBSUB_SINK",
                                value=f'{project_name}-ingestion-{target}',
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="PUBSUB_PROCEVENTS_SINK",
                                value=f'{project_name}-procevents-{target}',
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="PROJECT_NAME",
                                value=project_name
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="TARGET",
                                value=target
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="APPLICATION_PROJECT_ID",
                                value=project_id
                            ),
                        ]
                    )
                ]
            ),
        ),
    ),
)

service = kubernetes.core.v1.Service(
    "service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=app_name,
        labels={
            "krules.dev/app": app_name,
        },
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        selector={
            "krules.dev/app": app_name,
        },
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                port=80,
                target_port=8080
            )
        ]
    )
)

eventarc_firestore_trigger = gcp.eventarc.Trigger(
    "eventarc-firestore-trigger",
    project=cluster_project_id,
    service_account=base_stack_ref.get_output("gcp_cluster_project").apply(
        lambda project: f"{project['project_number']}-compute@developer.gserviceaccount.com"
    ),
    location=cluster_region,
    matching_criterias=[
        gcp.eventarc.TriggerMatchingCriteriaArgs(
            attribute="type",
            value="google.cloud.firestore.document.v1.written",
        ),
        gcp.eventarc.TriggerMatchingCriteriaArgs(
            attribute="database",
            value=sane_utils.get_var_for_target("FIRESTORE_DATABASE", default="(default)"),
        ),
    ],
    event_data_content_type="application/protobuf",
    destination=gcp.eventarc.TriggerDestinationArgs(
        gke=gcp.eventarc.TriggerDestinationGkeArgs(
            location=cluster_region,
            cluster=sane_utils.get_var_for_target("cluster", target),
            namespace=namespace,
            service=service.metadata.name,
            path="/"
        ),
    )
)
