import pulumi
import pulumi_gcp as gcp

from . import (
    project_name,
    target,
    cluster_project_id,
    namespace
)

gke_sa_default = gcp.serviceaccount.Account(
    "gke-sa-default",
    project=cluster_project_id,
    account_id=f"{project_name}-{target}-default",
    display_name=f"Default account for project {project_name}/{target}"
)

gke_sa_k8s_binding = gcp.serviceaccount.IAMBinding(
    "gke-sa-k8s-binding",
    service_account_id=gke_sa_default.email.apply(
        lambda email: f"projects/{cluster_project_id}/serviceAccounts/{email}"
    ),
    role="roles/iam.workloadIdentityUser",
    members=[
        f"serviceAccount:{cluster_project_id}.svc.id.goog[{namespace}/default]"
    ]
)

pulumi.export("gke_sa_default", gke_sa_default)
pulumi.export("gke_sa_k8s_binding", gke_sa_k8s_binding)
pulumi.export("bound_namespace", namespace)

