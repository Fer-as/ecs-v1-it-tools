resource "aws_security_group" "task" {
  name        = "${var.project_name}-ecs-task-sg"
  description = "Security group for ECS application tasks"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.project_name}-ecs-task-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_to_task" {
  security_group_id            = aws_security_group.task.id
  referenced_security_group_id = var.alb_security_group_id
  description                  = "Allow application traffic from the ALB"
  from_port                    = 8080
  to_port                      = 8080
  ip_protocol                  = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "task_outbound" {
  security_group_id = aws_security_group.task.id
  description       = "Allow outbound traffic through VPC routing"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}