import pulumi_gcp as gcp
import pulumi

from . import project_name, target, region, project_id, gcp_cluster_project

repository = gcp.artifactregistry.Repository(
    "artifact-registry",
     project=project_id,
     location=region,
     repository_id=f"{project_name}-{target}",
     format="DOCKER",
     labels={
         "target": target,
         "project_name": project_name,
     }
)


pulumi.export("docker_repository", repository)

bindings = gcp.organizations.get_iam_policy(
    bindings=[gcp.organizations.GetIAMPolicyBindingArgs(
        role="roles/artifactregistry.reader",
        members=[
                f"serviceAccount:{gcp_cluster_project.project_number}-compute@developer.gserviceaccount.com",
            ]
    )]
)

repo_policy = gcp.artifactregistry.RepositoryIamPolicy(
    "repo_policy",
    project=repository.project,
    location=repository.location,
    repository=repository.name,
    policy_data=bindings.policy_data
)

pulumi.export("repo_policy", repo_policy)
