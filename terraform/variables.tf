variable "project_name" {
    description = "The name of the project. This is not the Google project id which is target related"
    type = string
}

variable "primary_target" {
    description = "Primary target. Usually the first target in the list of targets"
    type = map
}

variable "targets" {
    description = "Deployment targets"
    type = map
}

variable "targets_with_cluster" {
    description = "Deployment targets"
    type = map
}

variable "all_projects" {
    description="All involved google projects"
    type = set(string)
}


