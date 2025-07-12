resource "aws_opensearch_domain" "logs" {
  domain_name    = "${local.project_name}-logs"
  engine_version = "OpenSearch_1.3"

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = var.opensearch_instance_count
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "admin"
      master_user_password = random_password.opensearch_password.result
    }
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${local.project_name}-logs/*"
      }
    ]
  })

  tags = local.common_tags
}

resource "random_password" "opensearch_password" {
  length  = 16
  special = true
}

# Store OpenSearch password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "opensearch_password" {
  name = "${local.project_name}-opensearch-password"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "opensearch_password" {
  secret_id = aws_secretsmanager_secret.opensearch_password.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.opensearch_password.result
  })
}