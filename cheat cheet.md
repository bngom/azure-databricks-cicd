# Cheat cheet

This is a step by Step walkthrough you can use to reproduce this experiment.

Clone the repository

```sh
git clone https://github.com/bngom/azure-databricks-cicd.git && cd azure-databricks-cicd
```

Create a python environment and install dependencies

```sh
python -m venv dbcicd
```

Activate the virtual environment

```sh
source dbcicd/bin/activate
```

Install requirements

```sh
pip install -r requirement.txt
```

Run lint test

```sh
python -m pip install flake8
flake8 ./test/ ./src/
```

Run unit test:

```sh
python -m test
```
> Note: Do this in the build pipeline phase and copy artifacts for the release step
Generating distribution archives for our library.

```
python3 -m pip install --upgrade build
python3 -m build
```

## Microsoft Azure

Here we are using [Azure Cloud Shell]() from the directry we want to deploy our resources. You can install [Azure CLI]() to perform the same task.


Configure Azure CLI, your difault browser will prompt for you to enter your credentials. This will connect you to your default tenant.

```sh
az login
```

Get details about your account. 

```sh
az account show
```

![](./assets/account-info.PNG)

You can now if you wish connect to a specific directory.

```sh
az login --tenant <TENANT ID>
```

### Prerequisites

In our selected directory let us Create a resource Group

```sh
az group create --name datatabricks-rg --location francecentral
```

Test the deployment against the resource group: this will only validate your template. The deployment will be done during the build phase in azure devops.

```sh
cd template
az deployment group what-if --name TestDeployment --resource-group databricks-rg --template-file dbx.template.json --parameters @dbx.parameters.json
```

## Setting up Azure DevOps

0. Go to dev.azure.com

1. [Create an Azure DevOps Organization](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization?view=azure-devops)

- Click on *New organization*, then click on Continue

![](./assets/neworg.png)

- Set the name of your Azure DevOps organization, then click on Continue.

![](./assets/dbx-cicd-org.png)


2. [Create a Project in your Azure DevOps Organisation](https://docs.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops&tabs=preview-page)

- In your new organization, set your project name then click on *Create project*

![](./assets/new-project.png)

3. Import a repository

- Click on *Repo*, then on *Import repository*

![](./assets/import-repo.png)

4. Set an Azure Resource Manager connection

- Project Settings > Pipeline : Service connections > Create service connections

![](./assets/create-service-connection.png)

- Select Azure Resource Manager

![](./assets/new-service-connections.png)

- Select *Service principal (automatique)*

![](./assets/new-service-connections-2.png)

- Select your subscription and the resource group `databricks-rg` created previously and save.

![](./assets/new-service-connections-3.png)


### Create a Build Pipeline

Follow these steps to create a build pipeline. This operation will generate artifacts for our release pipeline.

- Pipeline > Pipeline: CLick on Create pipeline
- Select *Azure GIt Repo*
- Select your repository
- Select *Python package*

The `azure-pipelines.yml` file in your repository is automatically detected

- Run your pipeline

![](./assets/build-pipeline-success.png)

Our build pipeline executed successfully and our artifacts are generated and ready to be consumed in a release pipelie.

![](./assets/summary-build.png)


Before Creating our release pipeline let us do some configuration in azure devops. For security purpose we have dummy varibale in our template parameter file. We will use our variable group to overwrite them in our release pipeline.

Create Variable Group:

- Pipeline > Library > +Variable Group

![](./assets/new-variable-grp.png)

- Create the following variable

![](./assets/variable-grp.png)



### Create a Release Pipeline

**Phase 1**

Create a release to deploy resources (Databricks workspace, KeyVault, Storage Account and Container for blob storage) on Microsoft Azure.

- Pipeline > Release: +New Piepline
- Update the Stage name to *Development*
- Add artifacts
- In variable: Link Variable Group for release and and stage
- In Task: Add ARM Resource Deployment and configure it accordingly giving the template and parameter files. And overwriting the variables:   
  - Deployment scope: Resource Group
  - Template: Click on `more` and select dbx.template.json in the template artifacts
  - Template parameters: select dbx.parameters.json in the template artifacts

```

```sh
# Override template parameters
-objectId "$(object_id)" -keyvaultName "$(keyvault)" -location "$(location)" -storageAccountName "$(sa_name)" -workspaceName "$(dbx_name)" -workspaceLocation "$(location)" -tier "premium" -sku "Standard" -tenant "$(tenant_id)" -networkAcls {"defaultAction":"Allow","bypass":"AzureServices","virtualNetworkRules":[],"ipRules":[]}
```

Generate a shared access signature token for the storage account. This will secure the communication between Azure Dtabricks and the object storage

```sh
end=`date -u -d "10080 minutes" '+%Y-%m-%dT%H:%MZ'`
az storage account generate-sas \
  --permissions lruwap \
  --account-name dbxbnsa \
  --services b \
  --resource-types sco \
  --expiry $end \
  -o tsv
```

Copy the SAS token generated and copy it into the key vault

```sh
az keyvault secret set --vault-name $keyvault_name --name "storagerw" --value "YOUR-SASTOKEN"
```

Let us few secrets in our the key vault

```sh
#Let us gather some variable
tenantId=$(az account list | jq '.[].tenantId')
userId=$(az ad user list --filter "startswith(displayName, 'Barthelemy Diomaye NGOM')" | jq '.[].objectId')
subscriptionId=$(az account subscription list | jq '.[].subscriptionId')
```

```sh
# Example: az keyvault secret set --vault-name $keyvault_name --name "ExampleSecret" --value "dummyValues"
# Set my tenant id as a secret
az keyvault secret set --vault-name $keyvault_name --name "tenantId" --value $tenantId

# Set my User id (Object ID) as a secret
az keyvault secret set --vault-name $keyvault_name --name "userId" --value $userId

# Set my Subscription id  as a secret 
az keyvault secret set --vault-name $keyvault_name --name "subscriptionId" --value $subscriptionId

az keyvault secret set --vault-name $keyvault_name --name "storageAccountName" --value "$storage_account"

az keyvault secret set --vault-name $keyvault_name --name "storageAccountContainer" --value "$container"

```

List your secrets

```sh
az keyvault secret list --vault-name $keyvault_name --output table
```



Create a cluster in databricks

```sh
cat <<EOF >> create-cluster.json
{
    "num_workers": null,
    "autoscale": {
        "min_workers": 1,
        "max_workers": 2
    },
    "cluster_name": "dbx-cluster",
    "spark_version": "8.2.x-scala2.12",
    "spark_conf": {},
    "azure_attributes": {
        "first_on_demand": 1,
        "availability": "ON_DEMAND_AZURE",
        "spot_bid_max_price": -1
    },
    "node_type_id": "Standard_DS3_v2",
    "ssh_public_keys": [],
    "custom_tags": {},
    "spark_env_vars": {
        "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
    },
    "autotermination_minutes": 120,
    "cluster_source": "UI",
    "init_scripts": []
}
EOF

databricks clusters create --json-file create-cluster.json
```


Get my key vault id to be used as reference in my arm template parameter's file

`az keyvault list | jq '.[].id'`


## Databricks CLI

Install Databricks cli [here](https://docs.databricks.com/dev-tools/cli/index.html)

Generate a databricks token [here](https://docs.databricks.com/dev-tools/api/latest/authentication.html#generate-a-personal-access-token)

Configure your cli to interact with databricks

```sh
databricks configure --token <GENERATED TOKEN>
```

Get the resource ID and the DNS name from your key vault properties

```sh
vaultUri=$(az keyvault show --name $keyvault_name | jq '.properties.vaultUri')
vaultId=$(az keyvault show --name $keyvault_name | jq '.id')
```

## Create an Azure Key Vault-backed secret scope

```sh
databricks secrets create-scope --scope demo-cicd --scope-backend-type AZURE_KEYVAULT --resource-id $vaultId --dns-name $vaultUri
```

## Resources

https://docs.python.org/fr/3/distributing/index.html
https://github.com/Azure-Samples/azure-sdk-for-python-storage-blob-upload-download
https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python-legacy
https://stackoverflow.com/questions/53217767/py4j-protocol-py4jerror-org-apache-spark-api-python-pythonutils-getencryptionen
https://docs.microsoft.com/fr-fr/azure/azure-resource-manager/templates/template-tutorial-use-key-vault
https://build5nines.com/azure-cli-2-0-generate-sas-token-for-blob-in-azure-storage/
https://docs.microsoft.com/fr-fr/azure/databricks/scenarios/store-secrets-azure-key-vault

