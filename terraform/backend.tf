terraform {
  backend "s3" {
    bucket       = "feras-ecs-it-tools-tfstate-670941257756"
    key          = "ecs-v1/dev/terraform.tfstate"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
  }
}
