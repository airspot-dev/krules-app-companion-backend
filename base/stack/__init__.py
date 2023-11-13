import pulumi
import pulumi_kubernetes as kubernetes

from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.components import (
    PubSubTopic,
    ArtifactRegistry, SaneDockerImage, FirestoreDB,
)

topic_ingestion = PubSubTopic("ingestion")
topic_procevents = PubSubTopic("procevents")
topic_firestore_updates = PubSubTopic("firestore-updates")
topic_settings = PubSubTopic("settings")

pulumi.export("topics", {
    "procevents": topic_procevents,
    "ingestion": topic_ingestion,
    "firestore-updates": topic_firestore_updates,
    "settings": topic_settings,
})

docker_registry = ArtifactRegistry(
    "docker-registry",
)
pulumi.export("docker-repository", docker_registry.repository)
pulumi.export("docker-cluster-artifact-iam-member", docker_registry.cluster_iam_member)

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

# firestore = FirestoreDB(
#     "firestore",
#     firestore_dbname=sane_utils.name_resource(sane_utils.check_env("project_name"))
# )
#
# pulumi.export("firestore", firestore.db)

# {
#   "app_engine_integration_mode": "DISABLED",
#   "concurrency_mode": "PESSIMISTIC",
#   "create_time": "",
#   "etag": "IIn5tqbgpYIDMLrqgabgpYID",
#   "id": "projects/companion-lab/databases/companion",
#   "key_prefix": "",
#   "location_id": "europe-west4",
#   "name": "companion",
#   "project": "companion-lab",
#   "type": "FIRESTORE_NATIVE",
#   "urn": "urn:pulumi:base-dev0::companion::sane:FirestoreDB$gcp:firestore/database:Database::firestore"
# }
