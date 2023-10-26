#!/usr/bin/env python3

from sane import sane_run

from krules_dev import sane_utils

sane_utils.load_env()

app_name = sane_utils.check_env("APP_NAME")
project_name = sane_utils.check_env("PROJECT_NAME")
target = sane_utils.get_target()


sane_utils.make_prepare_build_context_recipes(
    image_base="n3wscott/sockeye:v0.7.0",
)

sane_utils.make_pulumi_stack_recipes(
    app_name,
    configs={
        "gcp:project": sane_utils.get_project_id(),
        "kubernetes:context": sane_utils.get_var_for_target("kubectl_ctx", default=f"gke_{project_name}-{target}"),
        "base_stack": f"base-{target}",
    },
    up_deps=[
        ".build/Dockerfile"
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
