locals {
  rc_tags = {
    Name     = "${var.profile}-${var.eventbus_name}"
    env      = var.env
    profile  = var.profile
    author   = "rapid-cloud"
    fqn      = var.fqn
    cmd_id   = var.cmd_id
    workload = var.workload
  }

  eventbus_name = "${var.profile}-${var.eventbus_name}"
}
