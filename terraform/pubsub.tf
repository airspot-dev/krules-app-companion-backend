// Example: how to create Pub/Sub topic (See eventarc.tf example for events subscribing)

resource "google_pubsub_topic" "ingestion" {

  for_each = var.targets

  name = "app-companion-ingestion-${each.key}"
  project = "${each.value.project_id}"

  labels = {
    app = "${var.project_name}"
  }

  message_retention_duration = "86600s"
}

