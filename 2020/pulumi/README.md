# Pulumi

Tech Radar:
https://www.thoughtworks.com/radar/platforms?blipid=1283

Homepage:
https://www.pulumi.com/

Migrating from Terraform:
https://www.pulumi.com/edocs/guides/adopting/from_terraform/

## Demo

### Prereqs

- Have an AWS account created, and your `~/.aws/credentials` and `~/.aws/config` files set up.
- Add a ssh key to EC2 named `widget_store`.
- Add an entry to the Parameter Store at the path `/widget_store/test`.

### Install binaries

- `terraform`
- `pulumi`
- `tf2pulumi`

### Stand up terraform

Edit the `account_id` in `variables.tf` to your AWS account ID.

Make sure the `region` in `variables.tf` and `~/.aws/config` match.

Run `terraform apply`.

