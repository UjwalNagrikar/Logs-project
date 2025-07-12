# Kinesis Stream for log ingestion
resource "aws_kinesis_stream" "log_stream" {
  name        = "${local.project_name}-log-stream"
  shard_count = 1

  retention_period = 24

  shard_level_metrics = [
    "IncomingRecords",
    "OutgoingRecords",
  ]

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  tags = local.common_tags
}

# Kinesis Firehose for backup to S3
resource "aws_kinesis_firehose_delivery_stream" "log_backup" {
  name        = "${local.project_name}-log-backup"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.log_archive.arn
    prefix     = "logs/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"
    
    buffer_size     = 5
    buffer_interval = 300
    
    compression_format = "GZIP"
  }

  tags = local.common_tags
}

# IAM role for Kinesis Firehose
resource "aws_iam_role" "firehose_role" {
  name = "${local.project_name}-firehose-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "firehose.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "firehose_policy" {
  name = "${local.project_name}-firehose-policy"
  role = aws_iam_role.firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.log_archive.arn,
          "${aws_s3_bucket.log_archive.arn}/*"
        ]
      }
    ]
  })
}