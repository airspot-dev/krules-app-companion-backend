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
firestore_project_id = sane_utils.get_var_for_target('FIRESTORE_PROJECT_ID', target, default=project_id)
firestore_db_name = sane_utils.get_var_for_target('FIRESTORE_DB_NAME', target, default=f"{project_name}-{target}")

image = DockerImageBuilder(
    f"{app_name}-image",
    image_name=base_stack_ref.get_output('docker_repository').apply(
        lambda repository: f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}"
    ),
).build()

pulumi.export("image", image)


pull_subscription = gcp.pubsub.Subscription(
    f"{project_name}-{app_name}-{target}",
    topic=base_stack_ref.get_output("ingestion_topic").apply(lambda topic: topic["name"]),
    project=project_id,
    labels={
        "app_name": app_name,
        "project_name": project_name,
        "target": target,
    },
    message_retention_duration="600s",
    retain_acked_messages=False,
    ack_deadline_seconds=10,
    retry_policy=gcp.pubsub.SubscriptionRetryPolicyArgs(
        minimum_backoff="10s",
    ),
    enable_message_ordering=False
)

pulumi.export("pull_subscription", pull_subscription)

pull_subscription_subscriber_iam_member = gcp.pubsub.SubscriptionIAMMember(
    "pull_subscription_subscriber_iam_member",
    member=base_stack_ref.get_output("gke_sa_default").apply(lambda sa: f"serviceAccount:{sa['email']}"),
    role="roles/pubsub.subscriber",
    subscription=pull_subscription.name
)

deployment = kubernetes.apps.v1.Deployment(
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
                            kubernetes.core.v1.EnvVarArgs(
                                name="FIRESTORE_PROJECT_ID",
                                value=firestore_project_id
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="FIRESTORE_DATABASE",
                                value=firestore_db_name
                            ),
                        ],
                        # volume_mounts=[
                        #     kubernetes.core.v1.VolumeMountArgs(
                        #         mount_path="/var/secrets/firebase",
                        #         name="firebase-auth"
                        #     )
                        # ]
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        image=sane_utils.check_env("PULL_SUBSCRIBER_IMAGE"),
                        name="pull-subscriber",
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="SUBSCRIPTION",
                                value=pull_subscription.name
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="PROJECT",
                                value=project_id
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="CE_SINK",
                                value="http://localhost:8080"
                            ),
                            # kubernetes.core.v1.EnvVarArgs(
                            #     name="DEBUG",
                            #     value="1"
                            # ),
                        ]
                    )
                ],
                # volumes=[
                #     kubernetes.core.v1.VolumeArgs(
                #         name="firebase-auth",
                #         secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                #             secret_name="firebase-auth",
                #             # items=[
                #             #     kubernetes.core.v1.KeyToPathArgs(
                #             #         path="firebase-auth",
                #             #         key="firebase-auth"
                #             #     )
                #             # ]
                #         )
                #     )
                # ]
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


pulumi.export("ingestion-receiver-deployment", deployment)
pulumi.export("ingestion-receiver-service", service)
