import pulumi
import pulumi_kubernetes as kubernetes
from pulumi import Config, StackReference, Output

from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.components import DockerImageBuilder

# Initialize a config object
config = Config()

# Get the name of the "parent" stack that we will reference.
base_stack_ref = StackReference(config.require('base_stack'))

app_name = sane_utils.check_env("app_name")

image = DockerImageBuilder(
    f"{app_name}-image",
    image_name=base_stack_ref.get_output('docker_repository').apply(
        lambda repository: f"{repository['location']}-docker.pkg.dev/{repository['project']}/{repository['repository_id']}/{app_name}"
    ),
).build()

pulumi.export("image", image)

deployment = kubernetes.apps.v1.Deployment("deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name=app_name,
        labels={
            "krules.dev/app": app_name,
            "krules.dev/type": "ruleset"
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=int(sane_utils.get_var_for_target("celery_worker_replicas", default="1")),
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "krules.dev/app": app_name,
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "krules.dev/app": app_name,
                    "krules.dev/type": "ruleset"
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        image=image.repo_digest,
                        name=app_name,
                        env=[],  # TODO
                        env_from=[
                            kubernetes.core.v1.EnvFromSourceArgs(
                                secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
                                    name=base_stack_ref.get_output("celery_config_secret").apply(
                                        lambda secret: secret
                                    )
                                )
                            )
                        ]
                    )
                ],
            ),
        ),
    ),
)

pulumi.export("celery-worker-deployment", deployment)


