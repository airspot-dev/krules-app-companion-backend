import pulumi
import pulumi_kubernetes as kubernetes
import pulumi_gcp as gcp

from krules_dev import sane_utils
from krules_dev.sane_utils.pulumi.components import (
    PubSubTopic,
    ArtifactRegistry, SaneDockerImage, FirestoreDB,
)

topic_ingestion = PubSubTopic("ingestion")
topic_procevents = PubSubTopic("procevents")
topic_firestore_updates = PubSubTopic("firestore-updates")
topic_settings = PubSubTopic("settings")
topic_scheduler = PubSubTopic("scheduler") # events to be scheduled
topic_scheduler_errors = PubSubTopic("scheduler-errors")  # errors on scheduling jobs
topic_user_errors = PubSubTopic("user-errors")  # errors that somehow should be delivered to user (inconsistent input provided)

pulumi.export("topics", {
    "procevents": topic_procevents,
    "ingestion": topic_ingestion,
    "firestore-updates": topic_firestore_updates,
    "settings": topic_settings,
    "scheduler": topic_scheduler,
    "scheduler-errors": topic_scheduler_errors,
    "user-errors": topic_user_errors
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

gcp.firestore.Index(
    "firestore_idx_entity_asc",
    project=sane_utils.get_firestore_project_id(),
    database=sane_utils.get_firestore_database(),
    collection="data",
    query_scope="COLLECTION_GROUP",
    fields=[
        gcp.firestore.IndexFieldArgs(
            field_path="entity_id",
            order="ASCENDING"
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="datetime",
            order="ASCENDING",
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="__name__",
            order="ASCENDING",
        )
    ]
)

gcp.firestore.Index(
    "firestore_idx_entity_desc",
    project=sane_utils.get_firestore_project_id(),
    database=sane_utils.get_firestore_database(),
    collection="data",
    query_scope="COLLECTION_GROUP",
    fields=[
        gcp.firestore.IndexFieldArgs(
            field_path="entity_id",
            order="ASCENDING"
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="datetime",
            order="DESCENDING",
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="__name__",
            order="DESCENDING",
        )
    ]
)

gcp.firestore.Index(
    "firestore_idx_eventsource_entity_asc",
    project=sane_utils.get_firestore_project_id(),
    database=sane_utils.get_firestore_database(),
    collection="event_sourcing",
    query_scope="COLLECTION_GROUP",
    fields=[
        gcp.firestore.IndexFieldArgs(
            field_path="entity_id",
            order="ASCENDING"
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="datetime",
            order="ASCENDING",
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="__name__",
            order="ASCENDING",
        )
    ]
)

gcp.firestore.Index(
    "firestore_idx_eventsource_entity_desc",
    project=sane_utils.get_firestore_project_id(),
    database=sane_utils.get_firestore_database(),
    collection="event_sourcing",
    query_scope="COLLECTION_GROUP",
    fields=[
        gcp.firestore.IndexFieldArgs(
            field_path="entity_id",
            order="ASCENDING"
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="datetime",
            order="DESCENDING",
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="__name__",
            order="DESCENDING",
        )
    ]
)

gcp.firestore.Index(
    "firestore_idx_eventsource_props_asc",
    project=sane_utils.get_firestore_project_id(),
    database=sane_utils.get_firestore_database(),
    collection="event_sourcing",
    query_scope="COLLECTION_GROUP",
    fields=[
        gcp.firestore.IndexFieldArgs(
            field_path="changed_properties",
            array_config="CONTAINS"
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="datetime",
            order="ASCENDING",
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="__name__",
            order="ASCENDING",
        )
    ]
)

gcp.firestore.Index(
    "firestore_idx_eventsource_props_desc",
    project=sane_utils.get_firestore_project_id(),
    database=sane_utils.get_firestore_database(),
    collection="event_sourcing",
    query_scope="COLLECTION_GROUP",
    fields=[
        gcp.firestore.IndexFieldArgs(
            field_path="changed_properties",
            array_config="CONTAINS"
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="datetime",
            order="DESCENDING",
        ),
        gcp.firestore.IndexFieldArgs(
            field_path="__name__",
            order="DESCENDING",
        )
    ]
)


# TODO: not working (rules not updated) !!!!
firestore_rules = """\
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth.uid != null;
    }
  }
}
"""

gcp.firebaserules.Ruleset(
    "firestore_rules",
    project=sane_utils.get_firestore_project_id(),
    source=gcp.firebaserules.RulesetSourceArgs(
        files=[gcp.firebaserules.RulesetSourceFileArgs(
            content=firestore_rules,
            name="firestore.rules",
        )],
    ))
