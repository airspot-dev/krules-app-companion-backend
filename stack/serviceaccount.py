import pulumi
import pulumi_gcp as gcp

from . import (
    project_name,
    target,
    cluster_project_id,
    namespace,
    gcp_project
)

gke_sa_default = gcp.serviceaccount.Account(
    "gke-sa-default",
    project=gcp_project.project_id,
    account_id=f"{project_name}-default-{target}",
    display_name=f"Default account for project {project_name}/{target}"
)

gke_sa_k8s_binding = gcp.serviceaccount.IAMBinding(
    "gke-sa-k8s-binding",
    service_account_id=gke_sa_default.email.apply(
        lambda email: f"projects/{gcp_project.project_id}/serviceAccounts/{email}"
    ),
    role="roles/iam.workloadIdentityUser",
    members=[
        f"serviceAccount:{cluster_project_id}.svc.id.goog[{namespace}/default]"
    ]
)

gke_sa_service_account_celery_broker_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'gke_sa_service_account_secret_celery_broker_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-celery_broker-{target}",
    member=gke_sa_default.email.apply(
        lambda email: f"serviceAccount:{email}"
    ),
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

gke_sa_service_account_celery_results_backend_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'gke_sa_service_account_secret_celery_results_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-celery_results_backend-{target}",
    member=gke_sa_default.email.apply(
        lambda email: f"serviceAccount:{email}"
    ),
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

gke_sa_service_account_subjects_redis_url_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'gke_sa_service_account_secret_subjects_redis_url_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-subjects_redis_url-{target}",
    member=gke_sa_default.email.apply(
        lambda email: f"serviceAccount:{email}"
    ),
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

gke_sa_service_account_ingestion_api_key_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'gke_sa_service_account_secret_ingestion_api_key_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-ingestion_api_key-{target}",
    member=gke_sa_default.email.apply(
        lambda email: f"serviceAccount:{email}"
    ),
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

compute_service_account_celery_broker_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'compute_service_account_secret_celery_broker_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-celery_broker-{target}",
    member=f"serviceAccount:{gcp_project.project_number}-compute@developer.gserviceaccount.com",
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

compute_service_account_celery_results_backend_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'compute_service_account_secret_celery_results_backend_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-celery_results_backend-{target}",
    member=f"serviceAccount:{gcp_project.project_number}-compute@developer.gserviceaccount.com",
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

compute_service_account_subjects_redis_url_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'compute_service_account_secret_subjects_redis_url_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-subjects_redis_url-{target}",
    member=f"serviceAccount:{gcp_project.project_number}-compute@developer.gserviceaccount.com",
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

compute_service_account_ingestion_api_key_secret_iam_member = gcp.secretmanager.SecretIamMember(
    'compute_service_account_secret_ingestion_api_key_iam_member',
    secret_id=f"projects/{gcp_project.project_number}/secrets/{project_name}-ingestion_api_key-{target}",
    member=f"serviceAccount:{gcp_project.project_number}-compute@developer.gserviceaccount.com",
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

pulumi.export("gke_sa_default", gke_sa_default)
pulumi.export("gke_sa_k8s_binding", gke_sa_k8s_binding)
pulumi.export("bound_namespace", namespace)
