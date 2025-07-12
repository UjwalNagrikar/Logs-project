terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local values
locals {
  project_name = "logx"
  environment  = var.environment
  
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_kinesis_stream" "log_stream" {
  name        = "log-stream"
  shard_count = 1
}

resource "aws_lambda_function" "log_parser" {
  function_name = "log_parser"
  handler       = "log_parser.lambda_handler"
  runtime       = "python3.8"
  role          = aws_iam_role.lambda_exec.arn
  filename      = "lambda.zip"

  source_code_hash = filebase64sha256("lambda.zip")

  environment {
    KINESIS_STREAM_NAME = aws_kinesis_stream.log_stream.name
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      },
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_policy" {
  name       = "lambda_policy_attachment"
  roles      = [aws_iam_role.lambda_exec.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_api_gateway_rest_api" "log_api" {
  name        = "LogAPI"
  description = "API for searching logs"
}

resource "aws_api_gateway_resource" "search" {
  rest_api_id = aws_api_gateway_rest_api.log_api.id
  parent_id   = aws_api_gateway_rest_api.log_api.root_resource_id
  path_part   = "search"
}

resource "aws_api_gateway_method" "search_method" {
  rest_api_id   = aws_api_gateway_rest_api.log_api.id
  resource_id   = aws_api_gateway_resource.search.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "search_integration" {
  rest_api_id             = aws_api_gateway_rest_api.log_api.id
  resource_id             = aws_api_gateway_resource.search.id
  http_method             = aws_api_gateway_method.search_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.log_parser.invoke_arn
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.log_stream.name
}

output "api_gateway_url" {
  value = "${aws_api_gateway_rest_api.log_api.execution_arn}/search"
}