variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "logx"
}

variable "kinesis_stream_name" {
  description = "The name of the Kinesis stream"
  type        = string
  default     = "log-stream"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
  default     = "logParserFunction"
}

variable "api_gateway_name" {
  description = "The name of the API Gateway"
  type        = string
  default     = "logApiGateway"
}

variable "opensearch_domain_name" {
  description = "The name of the OpenSearch domain"
  type        = string
  default     = "log-opensearch"
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.small.search"
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch instances"
  type        = number
  default     = 1
}

variable "lambda_timeout" {
  description = "The timeout for the Lambda function in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "The memory size for the Lambda function in MB"
  type        = number
  default     = 128
}