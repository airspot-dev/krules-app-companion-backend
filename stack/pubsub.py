from . import project_name, target, project_id
from .serviceaccount import gke_sa_default
import pulumi
import pulumi_gcp as gcp


ingestion_topic = gcp.pubsub.Topic(
    f'{project_name}-ingestion-{target}',
    name=f'{project_name}-ingestion-{target}',
    project=project_id
)

topic_subscriber_iam_member = gcp.pubsub.TopicIAMMember(
    "ingestion-topic-subscriber",
    project=project_id,
    topic=ingestion_topic.name,
    role='roles/pubsub.subscriber',
    member=gke_sa_default.email.apply(lambda sa_email: f"serviceAccount:{sa_email}")
)


topic_publisher_iam_member = gcp.pubsub.TopicIAMMember(
    "ingestion-topic-publisher",
    project=project_id,
    topic=ingestion_topic.name,
    role='roles/pubsub.publisher',
    member=gke_sa_default.email.apply(lambda sa_email: f"serviceAccount:{sa_email}")
)

procevents_topic = gcp.pubsub.Topic(
    f'{project_name}-procevents-{target}',
    name=f'{project_name}-procevents-{target}',
    project=project_id
)

procevents_publisher_iam_member = gcp.pubsub.TopicIAMMember(
    "procevents-topic-publisher",
    project=project_id,
    topic=procevents_topic.name,
    role='roles/pubsub.publisher',
    member=gke_sa_default.email.apply(lambda sa_email: f"serviceAccount:{sa_email}")
)

pulumi.export('ingestion_topic', ingestion_topic)
pulumi.export('procevents_topic', procevents_topic)
