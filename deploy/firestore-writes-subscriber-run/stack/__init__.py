import pulumi
import pulumi_gcp as gcp
from pulumi import Config
from pulumi_gcp.artifactregistry import Repository
from pulumi_gcp.cloudrunv2 import ServiceTemplateContainerEnvArgs
from pulumi_gcp.eventarc import TriggerDestinationCloudRunServiceArgs

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference
from krules_dev.sane_utils.pulumi.components import CloudRun

config = Config()

app_name = sane_utils.check_env("app_name")

base_stack_ref = get_stack_reference("base")

gcp_repository = Repository.get(
    "gcp_repository",
    base_stack_ref.get_output(
        "docker-repository"
    ).apply(
        lambda repository: repository.get("id")
    )
)

topic_firestore_updates = gcp.pubsub.Topic.get(
    "firestore-updates",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("firestore-updates").get("id")
    )
)
topic_settings = gcp.pubsub.Topic.get(
    "settings",
    base_stack_ref.get_output(
        "topics"
    ).apply(
        lambda topics: topics.get("settings").get("id")
    )
)

service = CloudRun(
    app_name,
    gcp_repository=gcp_repository,
    service_kwargs=dict(
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
    ),
    publish_to={
        "firestore-updates": topic_firestore_updates,
        "settings": topic_settings,
    },
    subscribe_to={
        "firestore-trigger-created": dict(
            matching_criterias=[
                dict(
                    attribute="type",
                    value="google.cloud.firestore.document.v1.created",
                ),
                dict(
                    attribute="database",
                    value=sane_utils.get_firestore_database(),
                ),
                dict(
                    attribute="document",
                    operator="match-path-pattern",
                    value="{subscription=*}/groups/{group=*}/{document=*}"
                ),
            ],
            path="/entities/created"
        ),
        "firestore-trigger-updated": dict(
            matching_criterias=[
                dict(
                    attribute="type",
                    value="google.cloud.firestore.document.v1.updated",
                ),
                dict(
                    attribute="database",
                    value=sane_utils.get_firestore_database(),
                ),
                dict(
                    attribute="document",
                    operator="match-path-pattern",
                    value="{subscription=*}/groups/{group=*}/{document=*}"
                ),
            ],
            path="/entities/updated"
        ),
        "firestore-trigger-deleted": dict(
            matching_criterias=[
                dict(
                    attribute="type",
                    value="google.cloud.firestore.document.v1.deleted",
                ),
                dict(
                    attribute="database",
                    value=sane_utils.get_firestore_database(),
                ),
                dict(
                    attribute="document",
                    operator="match-path-pattern",
                    value="{subscription=*}/groups/{group=*}/{document=*}"
                ),

            ],
            path="/entities/deleted"
        ),
        "firestore-schema-changes": dict(
            matching_criterias=[
                dict(

                    attribute="type",
                    value="google.cloud.firestore.document.v1.written",
                ),
                dict(
                    attribute="database",
                    value=sane_utils.get_firestore_database(),
                ),
                dict(
                    attribute="document",
                    operator="match-path-pattern",
                    value="{subscription=*}/settings/schemas/{document=*}"
                ),
            ],
            path="/schemas"
        )

    },
    app_container_kwargs={
        "envs": [
            ServiceTemplateContainerEnvArgs(
                name="FIRESTORE_ID",
                value=sane_utils.get_firestore_id(),
            ),
        ]
    }
 )

pulumi.export("trigger", service.triggers)


# eventarc_firestore_trigger_written = gcp.eventarc.Trigger(
#     "eventarc-firestore-trigger-written",
#     matching_criterias=[
#         gcp.eventarc.TriggerMatchingCriteriaArgs(
#             attribute="type",
#             value="google.cloud.firestore.document.v1.written",
#         ),
#         gcp.eventarc.TriggerMatchingCriteriaArgs(
#             attribute="database",
#             value=sane_utils.get_firestore_database(),
#         ),
#     ],
#     event_data_content_type="application/protobuf",
#     destination=gcp.eventarc.TriggerDestinationArgs(
#         cloud_run_service=TriggerDestinationCloudRunServiceArgs(
#             service=service.service.name,
#             path="/written",
#         ),
#     )
# )