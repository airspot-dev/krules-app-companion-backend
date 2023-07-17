resource "google_pubsub_topic" "scheduled-events" {

  for_each = var.targets

  name = "${var.project_name}-scheduled-events-${each.key}"
  project = "${each.value.project_id}"

  labels = {
    app = "${var.project_name}"
  }

  message_retention_duration = "86600s"
}

resource "google_service_account" "scheduler-sa" {
  for_each = var.targets
  project = "${each.value.project_id}"
  account_id   = "scheduler-${data.google_project.projects[each.value.project_id].number}-${each.key}"
  display_name = "Scheduler service account"
}

resource "google_project_iam_member" "pubsub-scheduler-publisher-iam-binding" {
    for_each = var.targets
    project = "${each.value.project_id}"
    role     = "roles/pubsub.publisher"
    member = "serviceAccount:${google_service_account.scheduler-sa[each.key].email}"

    condition {
        title      = "for topic"
        expression = "resource.name == \"projects/${each.value.project_id}/topics/${var.project_name}-scheduled-events-${each.key}\""
    }
}
