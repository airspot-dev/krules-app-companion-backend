import pulumi
import pulumi_gcp as gcp
from pulumi import Config
from pulumi_gcp.artifactregistry import Repository
from pulumi_gcp.cloudrunv2 import ServiceTemplateContainerEnvArgs

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference
from krules_dev.sane_utils.pulumi.components import CloudRun

config = Config()

app_name = sane_utils.check_env("app_name")

base_stack_ref = get_stack_reference("base")

gcp_repository = Repository.get(
    "gcp_repository",
    base_stack_ref.require_output("docker-repository.id")
)


topic_firestore_updates = gcp.pubsub.Topic.get(
    "firestore-updates",
    base_stack_ref.require_output("topics.firestore-updates.id")
)

topic_settings = gcp.pubsub.Topic.get(
    "settings",
    base_stack_ref.require_output("topics.settings.id")
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
        "firestore-entity-changes": dict(
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
                    value="{subscription=*}/groups/{group=*}/{document=*}"
                ),
            ],
            path="/entities"

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
        ),
        "firestore-channel-changes": dict(
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
                    value="{subscription=*}/settings/channels/{document=*}"
                ),
            ],
            path="/channels"
        ),
        "firestore-triggers-changes": dict(
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
                    value="{subscription=*}/settings/automations/{document=*}"
                ),
            ],
            path="/triggers"
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
pulumi.export("image", service.image)

pulumi.export("trigger", service.triggers)


