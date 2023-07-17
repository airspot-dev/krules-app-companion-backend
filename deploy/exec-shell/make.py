#!/usr/bin/env python3
import os

from krules_dev import sane_utils

from sane import sane_run
from krules_dev.sane_utils import google


sane_utils.load_env()

#import pdb; pdb.set_trace()

def _get_image_base():
    if "KRULES_REPO_DIR" in os.environ:
        return sane_utils.get_buildable_image(
            location=os.path.join(os.environ["KRULES_REPO_DIR"], "images"),
            dir_name="ruleset-gcp-image-base",
        )
    return sane_utils.check_env("RULESET_IMAGE_BASE"),


sane_utils.google.make_target_deploy_recipe(
    image_base=_get_image_base,
    #baselibs=[
    #    "commons",
    #],
    #extra_target_context_vars={
    #    "subjects_redis_url": "SUBJECTS_REDIS_URL",
    #},
    sources=[
        "ruleset.py",
        ("ipython_config.py", "/root/.ipython/profile_default/"),
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