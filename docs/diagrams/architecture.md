# ECS v1 final architecture

AWS account `670941257756`, region `eu-west-2`. Solid links show application traffic or resource use; dashed links show deployment/control relationships. The hosted zone, S3 backend and OIDC bootstrap have separate lifecycles from the application Terraform root.

```mermaid
flowchart LR
    User[Browser] --> DNS[Route 53 A alias<br/>tm.feras-dev.co.uk]
    DNS --> ALB
    GitHub[GitHub Actions<br/>publish / deploy / destroy] -. OIDC token .-> OIDC[GitHub OIDC provider<br/>separate bootstrap]
    OIDC -. trust .-> Roles[Scoped GitHub IAM roles<br/>separate bootstrap]
    GitHub -. assumes .-> Roles
    Roles -. publishes image .-> ECR[ECR<br/>immutable SHA tag]
    Roles -. Terraform saved plan / native lock .-> S3[S3 backend<br/>versioned state + lockfile]
    Roles -. provisions application .-> ALB
    ACM[ACM certificate<br/>DNS validated] -. certificate .-> ALB
    DNS -. validation CNAME .-> ACM

    subgraph VPC[Application-managed VPC]
      IGW[Internet gateway]
      subgraph Public[Two public subnets]
        ALB[Public ALB<br/>HTTP 301 → HTTPS listener<br/>target group /health]
        NAT[NAT gateway + EIP<br/>in one public subnet]
      end
      subgraph Private[Two private subnets]
        ECS[ECS Fargate service<br/>private task, no public IP<br/>nginx :8080]
      end
      IGW --- ALB
      IGW --- NAT
      ALB -->|ALB SG → task SG, port 8080| ECS
      ECS -. outbound .-> NAT
    end

    ECR -. pulled image .-> ECS
    ECS -. application logs .-> CW[CloudWatch Logs]
```

The application Terraform root manages VPC, subnets/routes, NAT/EIP, ALB/listeners/target group, security groups, ECS resources, ECR, CloudWatch application logs, ACM and the application DNS records. The existing Route 53 hosted zone, S3 bucket/state history and separate GitHub OIDC/bootstrap infrastructure are retained across application destroy. One NAT gateway and one desired ECS task are configured; the two-subnet layout alone does not make the service fully redundant.
