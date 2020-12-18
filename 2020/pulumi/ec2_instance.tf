# Set up the EC2 instance
resource "aws_instance" "widget_store" {
  ami                  = data.aws_ami.widget_store_ami.id
  instance_type        = "t3a.nano"
  availability_zone    = "us-east-2b"
  iam_instance_profile = aws_iam_instance_profile.widget_store_instance_profile.id

  tags = {
    Name = "widget_store"
  }

  key_name = "widget_store"

  root_block_device {
    volume_size = 8
  }

  vpc_security_group_ids = [aws_security_group.widget_store.id]

  # The userdata script to call on each deploy
  user_data = file("./userdata.sh")
}
