# Terragrunt

https://www.thoughtworks.com/radar/tools?blipid=1266

https://terragrunt.gruntwork.io/

## Quick Terraform overview
- Configuration-as-Code
- Define anything you would manually configure in the AWS console or Google Cloud console as a config file instead.
- You can create the resource manually first, and then import it into Terraform later.
- You can group reusable code into modules, and set variables to be configured differently for each environment.

## Terraform pain points
- There used to be some real difficulty in using a module in one environment, but not in another.
  - For example, it was hard to create a Kubernetes cluster in the dev and prod environments, but not in qa.
  - Terraform 0.13 addresses the difficulty here by giving a way to disable a module with `count = 0`.

https://terragrunt.gruntwork.io/docs/getting-started/quick-start/
