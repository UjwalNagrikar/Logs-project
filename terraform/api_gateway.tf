resource "aws_api_gateway_rest_api" "log_api" {
  name        = "LogAPI"
  description = "API for accessing log data"
}

resource "aws_api_gateway_resource" "logs" {
  rest_api_id = aws_api_gateway_rest_api.log_api.id
  parent_id   = aws_api_gateway_rest_api.log_api.root_resource_id
  path_part   = "logs"
}

resource "aws_api_gateway_method" "get_logs" {
  rest_api_id   = aws_api_gateway_rest_api.log_api.id
  resource_id   = aws_api_gateway_resource.logs.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_logs_integration" {
  rest_api_id             = aws_api_gateway_rest_api.log_api.id
  resource_id             = aws_api_gateway_resource.logs.id
  http_method             = aws_api_gateway_method.get_logs.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.log_parser.invoke_arn
}

resource "aws_api_gateway_deployment" "log_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.log_api.id
  stage_name  = "prod"
}