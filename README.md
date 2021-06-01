# Azure Databricks CI/CD pipeline using Azure DevOps

Throughout the Development lifecycle of an application, [CI/CD] is a [DevOps] process enforcing automation in building, testing and desploying applications. Development and Operation teams can leverage the advantages of CI/CD to deliver more frequently and reliably releases in a timly manner while ensuring quick iterations.

CI/CD is becoming an increasingly necessary process for data engineering and data science teams to deliver valuable data project and increase confidence in the quality of the outcomes. With [Azure Databricks](https://azure.microsoft.com/en-gb/services/databricks/) you use solutions like Azure DevOps or Jenkins to build a CI/CD pipeline to reliably build, test, and deploy your notebooks and libraries.

In this article we will walk you trhought a development process ...

## Prerequisites

1. An Azure Account. You can create a free account [here]()

- Repos: Azure Devops Organization that will hold a project for our repository and our pipeline assets
- Azure Storage Account to store our dataset inside a blob container that will be used further
- SAS Token to authorize read and write to and from our blob container
- Azure Key Vault to store secrets(SAS Token, SA name)
- Azure Databrick token to allow CLI commands
- Setup secrets on Azure databricks to use them 

## Description of our ci/cd pipeline

- Continuous Integration: Build Pipeline

1. Pipeline > New Pipeline

```yml
# Generate a build artefact for our databricks workspace
trigger:
- dev

pool:
  vmImage: 'Ubuntu-16.04'

variables:
- name: notebook-name
  value: friends-notebook

steps:
- bash: |
    mkdir -p "$(Build.ArtifactStagingDirectory)/arm-template"
    cp databricks.workspace.parameters.json databricks.workspace.template.json "$(Build.ArtifactStagingDirectory)/arm-template/"
  displayName: 'ARM template Build Artifacts'
- bash: |
    mkdir -p "$(Build.ArtifactStagingDirectory)/notebook"
    cp notebook/$(notebook-name).py "$(Build.ArtifactStagingDirectory)/notebook/$(notebook-name)-$(Build.SourceVersion).py"
    cp notebook-run.json.tmpl "$(Build.ArtifactStagingDirectory)/notebook/notebook-run.json.tmpl"
  displayName: 'Notebook Build Artifacts'
- task: PublishBuildArtifacts@1
  displayName: Publish ARM Template Build Artifacts
  inputs:
    pathtoPublish: '$(Build.ArtifactStagingDirectory)/arm-template'
    artifactName: arm-template
- task: PublishBuildArtifacts@1
  displayName: Publish Notebook Build Artifacts
  inputs:
    pathtoPublish: '$(Build.ArtifactStagingDirectory)/notebook'
    artifactName: notebook

```

2. Create variables in Librairy

- Pipeline > Librairy


## Define the Build pipeline

- **Set up a build agent**
- `azure-pipelines.yml`

## Define the Release pipeline

## Conclusion

## Cheat Sheet

