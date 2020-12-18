# Pulumi

Tech Radar:
https://www.thoughtworks.com/radar/platforms?blipid=1283

Homepage:
https://www.pulumi.com/

Migrating from Terraform:
https://www.pulumi.com/docs/guides/adopting/from_terraform/

## Demo

### Start a new Pulumi project

```
pulumi new typescript -f
```

### Set up an ECR repo

https://www.pulumi.com/docs/aws/ecr/

### Run Pulumi

```
npm i --save @pulumi/aws
pulumi config set aws:region us-east-2
pulumi up
```
