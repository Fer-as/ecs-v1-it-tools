# ECS V1 – IT Tools Deployment

This project deploys the open-source **IT Tools** application to AWS using a containerised architecture.

The infrastructure is provisioned using **Terraform** and the application is deployed via **GitHub Actions CI/CD pipelines**.

The deployment includes:

* Docker containerisation
* Amazon ECS (Fargate)
* Amazon ECR
* Application Load Balancer
* ACM TLS certificates
* Route 53 DNS
* Terraform Infrastructure as Code
* GitHub Actions CI/CD

---

# Application

**IT Tools**

A collection of useful online tools for developers including:

* JSON formatter
* Base64 encoder / decoder
* Timestamp converter
* UUID generator
* and many more

Repository:

https://github.com/CorentinTh/it-tools

The source code is included in this project under the `app/` directory.

---

# Architecture

The application is deployed inside a custom VPC using ECS Fargate tasks behind an Application Load Balancer.

Traffic flow:

User → Route53 → ALB (HTTPS) → ECS Service → Container

Components used:

* VPC
* Public subnets
* Private subnets
* Application Load Balancer
* ECS Cluster
* ECS Service
* ECS Tasks
* ECR image repository
* ACM certificate
* Route53 DNS record

An architecture diagram will be included in the `docs/diagrams` directory.

---

# Infrastructure

Infrastructure is defined using **Terraform modules**.

Key features:

* Remote Terraform state stored in **S3**
* State locking enabled
* Modular Terraform structure
* ECS tasks deployed in **private subnets**
* HTTPS enabled using **ACM certificates**
* HTTP → HTTPS redirection via ALB

Infrastructure code is located in:

terraform/

---

# Local Setup

To run the application locally:

cd app
pnpm install
pnpm dev

The development server will start and the application will be available locally.

---

# Docker

Build the Docker image:

docker build -t ecs-it-tools ./app

Run the container locally:

docker run -p 8080:80 ecs-it-tools

Access the application at:

http://localhost:8080

---

# CI/CD Pipelines

CI/CD pipelines are implemented using **GitHub Actions**.

Pipelines include:

Application pipeline

* Docker image build
* Security scanning
* Push image to Amazon ECR

Infrastructure pipeline

* Terraform formatting and validation
* Infrastructure security scanning
* Terraform plan
* Terraform apply

Pipeline definitions are located in:

.github/workflows

---

# Deployment

The application is deployed using Terraform and ECS.

Deployment steps:

1. Build Docker image
2. Push image to ECR
3. Terraform provisions infrastructure
4. ECS pulls the image and deploys tasks
5. ALB routes HTTPS traffic to the service

---

# Live Demo

Once deployed, the application will be available via a custom domain.

Example:

https://tools.example.com

---

# Repository Structure

ecs-v1-it-tools

├── app
│   └── application source code

├── terraform
│   └── infrastructure modules

├── docs
│   ├── diagrams
│   └── screenshots

└── .github
└── workflows

---




