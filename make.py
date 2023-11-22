#!/usr/bin/env python3
import importlib

from sane import *

from krules_dev import sane_utils

sane_utils.load_env()

sane_utils.google.make_enable_apis_recipe(
    google_apis=[
        "compute",
        "artifactregistry",
        "secretmanager",
        "pubsub",
        "run",
        "firestore",
        "eventarc",
    ]
)

sane_utils.make_set_gke_context_recipe(
    fmt="gke_{project_name}-{target}",
    ns_fmt="{project_name}-{target}",
)

sane_utils.make_init_pulumi_gcs_recipes()

sane_utils.make_pulumi_stack_recipes(
    "base",
    program=lambda: importlib.import_module("base.stack"),
    configs={
        "gcp:project": sane_utils.get_var_for_target("project_id"),
        "kubernetes:context": sane_utils.get_kubectl_ctx(
            fmt="gke_{project_name}-{target}"
        )
    },
    up_deps=[
        "set_gke_context"
    ]
)

sane_utils.make_clean_recipe(
    globs=[

    ]
)


sane_run("pulumi_up")
