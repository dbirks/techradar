# Use the most recent Ubuntu 20.04 image
data "aws_ami" "widget_store_ami" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server*"]
  }

  owners = ["099720109477"] # Canonical
}
