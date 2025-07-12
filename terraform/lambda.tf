# Lambda function for log processing
resource "aws_lambda_function" "log_parser" {
  filename         = "lambda_function.zip"
  function_name    = "${local.project_name}-log-parser"
  role            = aws_iam_role.lambda_role.arn
  handler         = "log_parser.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 512

  environment {
    variables = {
      OPENSEARCH_ENDPOINT = aws_opensearch_domain.logs.endpoint
      S3_BUCKET          = aws_s3_bucket.log_archive.bucket
      INDEX_NAME         = "logs"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = local.common_tags
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.project_name}-log-parser"
  retention_in_days = 7

  tags = local.common_tags
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${local.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListStreams"
        ]
        Resource = aws_kinesis_stream.log_stream.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.log_archive.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpGet"
        ]
        Resource = "${aws_opensearch_domain.logs.arn}/*"
      }
    ]
  })
}

# Event Source Mapping for Kinesis
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.log_stream.arn
  function_name     = aws_lambda_function.log_parser.arn
  starting_position = "LATEST"
  batch_size        = 10
  
  depends_on = [aws_iam_role_policy.lambda_policy]
}

# S3 bucket for log archival
resource "aws_s3_bucket" "log_archive" {
  bucket = "${local.project_name}-log-archive-${random_id.bucket_suffix.hex}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "log_archive_versioning" {
  bucket = aws_s3_bucket.log_archive.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "log_archive_encryption" {
  bucket = aws_s3_bucket.log_archive.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}