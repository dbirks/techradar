# Set up the firewall rules
resource "aws_security_group" "widget_store" {
  name        = "widget_store"
  description = "Only allow certain traffic to the store"

  tags = {
    Name = "Widget Store"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "ssh from anywhere"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
}
