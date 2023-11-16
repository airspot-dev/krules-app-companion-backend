#!/usr/bin/env python3

from sane import sane_run

from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.shell import get_stack_outputs

sane_utils.load_env()

app_name = sane_utils.check_env("APP_NAME")
project_name = sane_utils.check_env("PROJECT_NAME")
target = sane_utils.get_target()

base_outputs = get_stack_outputs("base")

sane_utils.make_prepare_build_context_recipes(
    image_base=lambda: None,
    sources=[
        "src",
        "angular.json",
        "firebase.json",
        "nginx-default.conf",
        "package.json",
        "package-lock.json",
        "tsconfig.app.json",
        "tsconfig.json",
        "tsconfig.spec.json",
    ],
)

sane_utils.make_render_resource_recipes(
    out_dir=".build/src",
    globs=[
        "src/firebase_config.json.j2"
    ],
    context_vars=lambda: {k: sane_utils.check_env(k) for k in (
        "firebase_api_key",
        "firebase_auth_domain",
        "firebase_project_id",
        "firebase_storage_bucket",
        "firebase_messaging_sender_id",
        "firebase_app_id",
    )}
)

sane_utils.make_pulumi_stack_recipes(
    app_name,
    configs={
        "gcp:project": sane_utils.get_var_for_target("project_id"),
        "kubernetes:context": sane_utils.get_var_for_target("kubectl_ctx", default=f"gke_{project_name}-{target}"),
        "base_stack": f"base-{target}"
    },
    up_deps=[
        ".build/src/firebase_config.json",
        ".build/Dockerfile",
    ]
)

# clean
sane_utils.make_clean_recipe(
    name="clean",
    globs=[
        ".build",
    ],
)

sane_run("pulumi_up")
