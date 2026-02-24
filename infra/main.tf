terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_dynamodb_table" "posted_articles" {
  name         = "PostedArticles"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "url"

  attribute {
    name = "url"
    type = "S"
  }

  tags = {
    Project = "sloth_feed"
  }
}

output "table_name" {
  value = aws_dynamodb_table.posted_articles.name
}

output "table_arn" {
  value = aws_dynamodb_table.posted_articles.arn
}
