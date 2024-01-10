resource "aws_cloudwatch_event_bus" "messenger" {
  name = local.eventbus_name
}