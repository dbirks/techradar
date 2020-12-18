# Create a static IP
resource "aws_eip" "widget_store" {
  tags = {
    "Name" = "widget_store"
  }
}

# Associate the static IP with the instance
resource "aws_eip_association" "public_ip_association" {
  instance_id   = aws_instance.widget_store.id
  allocation_id = aws_eip.widget_store.id
}
