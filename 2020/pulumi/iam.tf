# Set up a IAM instance profile, role, and policy for the EC2 instance to run as
resource "aws_iam_instance_profile" "widget_store_instance_profile" {
  name = "widget_store_instance_profile"
  role = aws_iam_role.widget_store_role.name
}

resource "aws_iam_role" "widget_store_role" {
  name = "widget_store_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "widget_store_policy" {
  name = "widget_store_policy"
  role = aws_iam_role.widget_store_role.name

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParametersByPath"
      ],
      "Resource": "arn:aws:ssm:${var.region}:${var.account_id}:parameter/widget_store/*"
    }
  ]
}
POLICY
}

# Allow EC2 Session Manager to connect
resource "aws_iam_role_policy_attachment" "widget_store_ssm" {
  role = aws_iam_role.widget_store_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
