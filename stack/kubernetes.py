import pulumi
from pulumi_kubernetes.core.v1 import Namespace, Secret, ServiceAccount, ServiceAccountPatch
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs, ObjectMetaPatchArgs

from krules_dev import sane_utils

celery_broker = sane_utils.get_google_secret("celery_broker").decode()
celery_results_backend = sane_utils.get_google_secret("celery_results_backend").decode()
firebase_auth = sane_utils.get_google_secret("firebase_auth").decode()

project_name = sane_utils.check_env("project_name")
target, _ = sane_utils.get_targets_info()

ns_name = sane_utils.get_var_for_target("namespace", default=f"{project_name}-{target}")

namespace = Namespace(
    'project-namespace',
    metadata={
        'name': ns_name
    }
)

pulumi.export("namespace", namespace.metadata['name'])

# annotate default sa for google workload identity
from .serviceaccount import gke_sa_default
k8s_default_sa_patch = ServiceAccountPatch(
    "k8s-patch-default-sa",
    metadata=ObjectMetaPatchArgs(
        name="default",
        annotations={
            "iam.gke.io/gcp-service-account": gke_sa_default.email.apply(lambda email: email)
        }
    ),
)

pulumi.export("k8s_default_sa", k8s_default_sa_patch)

# creating a secret resource
celery_config_secret = Secret(
    'celery-config-secret',
    metadata={
        'name': "celery-config"},
    type="Opaque",
    string_data={
        'CELERY_BROKER': celery_broker,
        'CELERY_RESULTS_BACKEND': celery_results_backend,
    }
)

firebase_auth_secret = Secret(
    'firebase-auth-secret',
    metadata={
        'name': 'firebase-auth'
    },
    type="Opaque",
    string_data={
        'firebase-auth': firebase_auth
    }
)

pulumi.export('celery_config_secret', celery_config_secret.metadata['name'])
pulumi.export('firebase_auth_secret', firebase_auth_secret.metadata['name'])
