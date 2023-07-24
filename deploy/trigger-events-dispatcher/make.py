#!/usr/bin/env python3
import os

from krules_dev import sane_utils

from sane import sane_run
from krules_dev.sane_utils import google


sane_utils.load_env()


sane_utils.google.make_target_deploy_recipe(
    image_base="python:3.10-slim-bullseye",
    extra_context_vars={
        # "redis_connection_url": "SUBJECTS_REDIS_URL",
        "region": sane_utils.check_env("REGION")
    },
    sources=[
        ("main.py", "/"),
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
