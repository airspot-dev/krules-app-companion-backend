#!/usr/bin/env python3
import os

from krules_dev import sane_utils

from sane import sane_run
from krules_dev.sane_utils import google


sane_utils.load_env()


sane_utils.google.make_target_deploy_recipe(
    image_base="gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.1.0",
    #baselibs=[
    #    "commons",
    #],
    extra_target_context_vars={
        "sql_instance": "SQL_INSTANCE",
        "sql_port": "SQL_PORT"
    },
    sources=[],
)

# clean
sane_utils.make_clean_recipe(
    name="clean",
    globs=[
        ".build",
    ],
)

sane_run("deploy")