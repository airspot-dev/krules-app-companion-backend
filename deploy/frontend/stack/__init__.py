import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as kubernetes
from pulumi import Config

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


deployment = GkeDeployment(
    app_name,
    service_type="ClusterIP",
    service_spec_kwargs={
        "ports": [kubernetes.core.v1.ServicePortArgs(
            port=80,
            protocol="TCP",
            target_port=80
        )]
    },
    gcp_repository=gcp_repository,
)

pulumi.export("service", deployment.service)


