from krules_dev import sane_utils
from pulumi_google_native.cloudresourcemanager import v1

import pulumi

project_name = sane_utils.check_env("PROJECT_NAME")

target, _ = sane_utils.get_targets_info()
project_id = sane_utils.get_var_for_target('PROJECT_ID', target, True)
region = sane_utils.get_var_for_target('REGION', target, True)
namespace = sane_utils.get_var_for_target("NAMESPACE", target, default=f"{project_name}-{target}")

cluster_project_id = sane_utils.get_var_for_target("CLUSTER_PROJECT_ID", target, default=project_id)
cluster_region = sane_utils.get_var_for_target("CLUSTER_REGION", target, default=region)

gcp_project = v1.get_project(project=project_id)
gcp_cluster_project = gcp_project
if project_id != cluster_project_id:
    gcp_cluster_project = v1.get_project(project=cluster_project_id)

vpcaccess_connector_project_id = sane_utils.get_var_for_target("VPCACCESS_CONNECTOR_PROJECT_ID")

pulumi.export("gcp_project", gcp_project)
pulumi.export("gcp_cluster_project", gcp_cluster_project)

from .repository import *
from .serviceaccount import *
from .kubernetes import *
from .vpcaccess import *
from .pubsub import *
