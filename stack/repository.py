import pulumi_gcp as gcp
import pulumi

from . import *

repository = gcp.artifactregistry.Repository(
    "artifact-registry",
     location=region,
     repository_id=f"{project_name}-{target}",
     format="DOCKER",
     labels={
         "target": target,
         "project_name": project_name,
     }
)


pulumi.export("repository_name", repository.name)
