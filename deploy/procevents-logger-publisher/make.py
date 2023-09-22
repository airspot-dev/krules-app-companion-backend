#!/usr/bin/env python3

from krules_dev import sane_utils

from sane import sane_run

sane_utils.load_env()

krules_dev.sane_utils.google.google.make_cloud_deploy_recipes(
    image_base=sane_utils.check_env("RULESET_IMAGE_BASE"),
    baselibs=[],
    sources=[
        "ruleset.py",
        "routers.py",
    ],
)

# clean
sane_utils.make_clean_recipe(
    name="clean",
    globs=[
        ".build",
        ".kpt-pipeline",
    ],
)

sane_run("deploy")
