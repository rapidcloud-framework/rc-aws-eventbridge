resource "aws_cloudwatch_event_rule" "this" {
  name        = local.eventrule_name
  event_bus_name = var.eventbus_name
  event_pattern       = var.event_pattern
  #schedule_expression = lookup(each.value, "schedule_expression", null)
  role_arn            = var.role_arn

}

resource "aws_cloudwatch_event_target" "target" {
  rule      = local.eventrule_name
  event_bus_name = var.eventbus_name
  target_id = "custom_target"
  arn       = var.custom_target_arn
  depends_on = [ aws_cloudwatch_event_rule.this ]
}
