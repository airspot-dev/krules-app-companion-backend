#!/usr/bin/env python3

from krules_dev import sane_utils

from sane import sane_run
from krules_dev.sane_utils import google


sane_utils.load_env()

sane_utils.make_render_resource_recipes(
    globs=[
        'Dockerfile.j2',
    ],
    context_vars=lambda: {
        "image_base": sane_utils.check_env("GENERIC_IMAGE_BASE"),
    },
    hooks=[
        'prepare_build'
    ]
)

google.make_cloud_build_recipe(
    name="build_and_push",
    project=sane_utils.check_env("PROJECT_ID"),
    artifact_registry=sane_utils.check_env("ARTIFACT_REGISTRY"),
    image_name="celery-worker",
    dockerfile_path=".build",
    hook_deps=[
        'prepare_build',
    ]
)


# clean
sane_utils.make_clean_recipe(
    name="clean",
    globs=[
        ".build",
    ],
)

sane_run()