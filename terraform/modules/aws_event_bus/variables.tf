# generic 
variable "env" {}
variable "profile" {}
variable "workload" {}
variable "fqn" {}
variable "cmd_id" { default = "" }

# Event Bus
variable "eventbus_name" {
  type        = string
  description = "(Required) The name of the new event bus. The names of custom event buses can't contain the / character"
}
# variable "event_source_name " {
#   type = string
#   description = "(Optional) The partner event source that the new event bus will be matched with. Must match name"
# }
variable "tags" { default = {} }
