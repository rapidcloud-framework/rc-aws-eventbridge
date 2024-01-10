# generic 
variable "env" {}
variable "profile" {}
variable "workload" {}
variable "fqn" {}
variable "cmd_id" { default = "" }

# Event Rule
variable "tags" { default = {} }

variable "eventrule_name" {
  type        = string
  description = "(Optional) The name of the rule. If omitted, Terraform will assign a random, unique name. Conflicts with name_prefix"
}

variable "eventbus_name" {
  type = string
  description = "Name of the event bus to be associated with the rule"
  
}

variable "event_pattern" {
  type = string
}

variable "description" {
  type        = string
  description = "(Optional) The description of the rule"
  default     = null
}

variable "role_arn" {
  type = string
  description = "Role ARN to be used to invoke the target"
}

variable "custom_target_arn" {
  type = string
  description = "ARN of the target to be invoked"
}