terraform {
  backend "s3" {
    bucket         = "feras-ecs-it-tools-tfstate"
    key            = "ecs-v1/dev/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "ecs-it-tools-tf-locks"
    encrypt        = true
  }
}
