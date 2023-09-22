#!/usr/bin/env python3

from sane import *

from krules_dev import sane_utils
from krules_dev.sane_utils import google

sane_utils.load_env()

STACK_NAME = f"base-{sane_utils.get_targets_info()[0]}"

sane_utils.google.make_enable_apis_recipe(
    google_apis=[
        "artifactregistry",
    ]
)

sane_utils.google.make_set_gke_context_recipe()

sane_utils.google.make_init_pulumi_gcs_recipes()

sane_utils.make_pulumi_stack_recipes(
    stack_name=STACK_NAME,
    configs={
        "gcp:project": sane_utils.get_var_for_target("project_id")
    }
)

sane_utils.make_clean_recipe(
    globs=[

    ]
)


sane_run()
