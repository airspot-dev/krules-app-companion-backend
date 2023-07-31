#!/usr/bin/env python3

from krules_dev import sane_utils

from sane import sane_run
from krules_dev.sane_utils import google
import os

sane_utils.load_env()

def _get_image_base():
    if "KRULES_REPO_DIR" in os.environ:
        return sane_utils.get_buildable_image(
            location=os.path.join(os.environ["KRULES_REPO_DIR"], "images"),
            dir_name="ruleset-gcp-image-base",
        )
    return sane_utils.check_env("RULESET_IMAGE_BASE")

sane_utils.google.make_target_deploy_recipe(
    #image_base=sane_utils.check_env("RULESET_IMAGE_BASE"),
    image_base=_get_image_base,
    baselibs=[
        "common"
    ],
    sources=[
        "middlewares.py",
        "ruleset.py",
        "routers.py"
    ],
)

# clean
sane_utils.make_clean_recipe(
    name="clean",
    globs=[
        ".build",
    ],
)

sane_run("deploy")
