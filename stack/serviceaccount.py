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

gke_sa_service_account_user_iam_member = gcp.projects.IAMMember(
    'gke_sa_service_account_user_iam_member',
    member=gke_sa_default.email.apply(
        lambda email: f"serviceAccount:{email}"
    ),
    project=gcp_project.project_id,
    role="roles/secretmanager.secretAccessor"
)

pulumi.export("gke_sa_default", gke_sa_default)
pulumi.export("gke_sa_k8s_binding", gke_sa_k8s_binding)
pulumi.export("bound_namespace", namespace)

