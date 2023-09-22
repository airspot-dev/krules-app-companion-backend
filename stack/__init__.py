from krules_dev import sane_utils


project_name = sane_utils.check_env("PROJECT_NAME")

target, _ = sane_utils.get_targets_info()
project_id = sane_utils.get_var_for_target('PROJECT_ID', target, True)
region = sane_utils.get_var_for_target('REGION', target, True)
namespace = sane_utils.get_var_for_target("NAMESPACE", target, default=f"{project_name}-{target}")

cluster_project_id = sane_utils.get_var_for_target("CLUSTER_PROJECT_ID", target, default=project_id)

from .repository import *
from .serviceaccount import *