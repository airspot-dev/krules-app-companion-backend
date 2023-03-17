resource "google_service_account" "gke-sa-default" {
  for_each = var.targets_with_cluster
  project = "${each.value.project_id}"
  account_id   = "${var.project_name}-${each.key}-default"
  display_name = "default service account for target ${each.key}"
}

resource "google_service_account_iam_binding" "goog-id-iam-binding-default" {
    for_each = var.targets_with_cluster
    service_account_id = "projects/${each.value.project_id}/serviceAccounts/${var.project_name}-${each.key}-default@${each.value.project_id}.iam.gserviceaccount.com"
    role               = "roles/iam.workloadIdentityUser"

    members = [
      "serviceAccount:${each.value.project_id}.svc.id.goog[${each.value.namespace}/default]",
    ]
}

resource "google_project_iam_member" "cloudrun-secret-manager-iam-binding" {
    for_each = var.all_projects
    project = "${each.key}"
    role     = "roles/secretmanager.secretAccessor"
    member   = "serviceAccount:${data.google_project.projects[each.key].number}-compute@developer.gserviceaccount.com"
}

// Some examples of IAM role binding
/*
resource "google_project_iam_member" "firebase-admin-iam-binding" {
    for_each = var.targets
    project = "${each.value.project_id}"
    role     = "roles/firebase.admin"
    member   = "serviceAccount:${google_service_account.gke-sa-default[each.key].email}"
}

resource "google_project_iam_member" "logwriter-iam-binding" {
    for_each = var.targets
    project = "${each.value.project_id}"
    role     = "roles/logging.logWriter"
    member   = "serviceAccount:${google_service_account.gke-sa-default[each.key].email}"
}
*/
