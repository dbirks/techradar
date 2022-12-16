# Paperspace Gradient

Tech radar: https://www.thoughtworks.com/radar/platforms?blipid=202210070

Homepage: https://www.paperspace.com/gradient

Documentation: https://docs.paperspace.com/gradient/

## Description

A Machine Learning platform, made up of three main pieces:
  - Notebooks
    - [Tutorial](https://docs.paperspace.com/gradient/tutorials/notebooks-tutorial)
    - similar to Jupyter notebooks, customized
    - has persistent storage backing it
    - keeps a history of the workspace changes, with ability to roll back
    - can connect to the remote Jupyter kernel with VSCode
    - optionally able to be opened as an upstream JupyterLab notebook
    - also has a terminal
  - Workflows
    - [Tutorial](https://docs.paperspace.com/gradient/tutorials/workflows-tutorial)
    - a pipeline tool to give a single pane of glass on the ML process
    - configurable with yaml ([link](https://docs.paperspace.com/gradient/workflows/workflow-spec))
    - based on the open source Argo Workflows
    - Reminds me of Github Actions (Gradient Actions [docs](https://docs.paperspace.com/gradient/workflows/gradient-actions))
  - Deployments
    - [Tutorial](https://docs.paperspace.com/gradient/tutorials/deployments-tutorial)
    - for hosting the trained model
    - you can define a deployment spec in yaml ([link](https://docs.paperspace.com/gradient/deployments/deployment-spec))

But also including:
  - Models
  - Connections to external container registries
  - Metrics & logs
  - Secrets

## Alternatives

- Google Colab
- AWS SageMaker
  - SageMaker Notebooks =~ Gradient Notebooks
  - SageMaker Endpoints =~ Gradient Deployments
- Google Cloud Vertex AI

## Pros

- Notebooks have persistent storage attached
- A simple, clean interface
- Good support via email on paid plan
- It looks like there's no extra ingress/egress charges

## Cons

- Storage limitations
  - 5 GB for free tier
  - 15 GB for the $8/month tier
  - with the overage charges being $0.29 per GB a month
- Free tier is not guaranteed (similar to Google Colab, to be expected)

## Recommendation

Tech Radar recommendation: Assess
My recommendation: Trial
