#!/bin/sh

# Echo commands as they're run, with environment variables expanded
set -o xtrace

# Exit if any command errors
set -o errexit

# Install dependencies
apt install -y nginx

# Set up our test page
aws ssm get-parameter --name /widget_store/test --with-decryption --output text --query Parameter.Value > /usr/share/nginx/html/index.html

# Start services
systemctl enable --now nginx
