import pulumi
import pulumi_kubernetes as kubernetes

from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.components import (
    PubSubTopic,
    ArtifactRegistry, SaneDockerImage, FirestoreDB,
)

topic_ingestion = PubSubTopic("ingestion")
topic_procevents = PubSubTopic("procevents")
topic_defaultsink = PubSubTopic("defaultsink")

pulumi.export("topics", {
    "procevents": topic_procevents,
    "defaultsink": topic_defaultsink,
    "ingestion": topic_ingestion,
})

docker_registry = ArtifactRegistry(
    "docker-registry",
)
pulumi.export("docker-repository", docker_registry.repository)

namespace = kubernetes.core.v1.Namespace(
    "gke-namespace",
    metadata={
        "name": sane_utils.get_namespace()
    }
)
pulumi.export("gke-namespace", namespace)

ruleset_base_image = SaneDockerImage(
    "ruleset-base",
    gcp_repository=docker_registry.repository,
    context="base/images/ruleset",
)

pulumi.export("ruleset-image-base", ruleset_base_image.image)

firestore = FirestoreDB(
    "firestore",
)

pulumi.export("firestore", firestore.db)
