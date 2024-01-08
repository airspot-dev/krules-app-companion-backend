#!/usr/bin/env python3
import importlib
import logging
import os

import sh
import structlog
from sane import *
from structlog.contextvars import bind_contextvars

from krules_dev import sane_utils

sane_utils.load_env()

root_dir = os.environ["KRULES_PROJECT_DIR"]

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


@recipe(name="update_all", info="Update all components")
def update_all():
    log = structlog.get_logger()
    python = sh.Command(sane_utils.check_cmd("python3"))

    def _make():
        log.info(f"Running make.py in {os.getcwd()}")
        python.bake("make.py")(_fg=True)

    with sh.pushd(root_dir):
        _make()
    with sh.pushd(os.path.join(root_dir, "deploy")):
        with sh.pushd("backend-api"):
            _make()
        with sh.pushd("firebase-authadmin"):
            _make()
        with sh.pushd("procevents-logger-publisher"):
            _make()
        with sh.pushd("firestore-writes-subscriber-run"):
            _make()
        with sh.pushd("settings-updater"):
            _make()
        with sh.pushd("firestore-entity-states"):
            _make()
        with sh.pushd("firestore-eventsourcing"):
            _make()
        with sh.pushd("scheduler-receiver"):
            _make()
        with sh.pushd("celery-worker"):
            _make()
        with sh.pushd("frontend"):
            _make()
        with sh.pushd("gke-ingress"):
            _make()


sane_utils.make_clean_recipe(
    globs=[

    ]
)

sane_run("pulumi_up")
