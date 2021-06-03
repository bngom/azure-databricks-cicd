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

- Create the following variable, and save

![](./assets/variable-grp.png)


### Create a Release Pipeline

**Phase 1**

Create a release to deploy resources (Databricks workspace, KeyVault, Storage Account and Container for blob storage) on Microsoft Azure.

- Pipelines > Release: +New Piepline
- On the right blade, For select a template click on *Empty Job*

![](./assets/empty-job.png)

- Update the Stage name to *Development*

![](./assets/stage-dev.png)

- Click on *Add artifacts* and Select the source build pipeline `demo-cicd`. The click on *Add*

![](./assets/add-artifacts.png)

- Click on variable and link our Variable Group to stage Development

![](./assets/link-variable-grp.png)

![](./assets/link-variable-grp-2.png)

- Now, click on  Task: 
  - Check the Agent job set up: make sure the Agent Specification is set to `ubuntu-20.04`
  - Clic on + sign near Agent job 

![](./assets/plus-task.png)

  - Add ARM Resource Deployment and configure it accordingly giving the template and parameter files. And overwriting the variables:   
    - Deployment scope: Resource Group
    - Select your Azure Resource manager connection and click on Authorize
    - Select your subscription
    - Action: Create or update resource group
    - Resource group: select the resource group created previously or use the variable $(rg_name)
    - Location: idem, or $(location)
    - Template: Click on `more` and select `dbx.template.json` in the template artifacts
    - Template parameters: select `dbx.parameters.json`in the template artifacts
    - Override template parameters:

    Or you can copy past the below lines of code

    ![](./assets/arm-template-deployment.png)

    ```sh
    -objectId $(object_id) -keyvaultName $(keyvault) -location $(location) -storageAccountName $(sa_name) -containerName $(container) -workspaceName $(workspace) -workspaceLocation $(location) -tier "premium" -sku "Standard" -tenant $(tenant_id) -networkAcls {"defaultAction":"Allow","bypass":"AzureServices","virtualNetworkRules":[],"ipRules":[]}
    ```
    - Deployment mode: Incremental
    - Now, save your configuration

    ![](./assets/template-parameters.png)

Now, create a first release

- Click on the button: Create release

![](./assets/create-release-btn.png)

- Stages for a trigger change from automated to manual: select Development

![](./assets/new-release.png)

- Click on create
- Go to Pipelines > Release
- Select our release pipeline 
![](./assets/select-release.png)

- Click on the newly created release
![](./assets/deploy-release.png)

![](./assets/deploy-release-1.png)

- Click on deploy

![](./assets/deploy-release-2.png)

Our pipeline executed successfully

![](./assets/release-pipeline-success.png)

And our resources are deployed in Azure. Go to Azure Portal and check

![](./assets/check-az-resources.png)


**Phase 2**

We will complete the deployment of our release pipeline but let us do some configuration.

Install Databricks cli [here](https://docs.databricks.com/dev-tools/cli/index.html)

Launch your Databricks workspace and generate an Access Token

Generate a databricks token [here](https://docs.databricks.com/dev-tools/api/latest/authentication.html#generate-a-personal-access-token)

Copy the new token and save it into your keyvault. At the same tiime we will save the URI of our Databricks service, you can find this one in Azure portal 



```sh
export dbxtoken="dapiee3855ad0418b23ec57b2833f8536472"
export dbxuri="https://adb-620934829532625.5.azuredatabricks.net" 
# uri="https://adb-<workspace-id>.<random-number>.azuredatabricks.net"
az keyvault secret set --vault-name $keyvault_name --name "dbxtoken" --value $dbxtoken
az keyvault secret set --vault-name $keyvault_name --name "dbxuri" --value $dbxuri
```

Generate a shared access signature token for the storage account. This will secure the communication between Azure Dtabricks and the object storage

```sh
a_name="dbxbnsa"
keyvault_name="dbx-bn-keyvault"
end=`date -u -d "10080 minutes" '+%Y-%m-%dT%H:%MZ'`
az storage account generate-sas \
  --permissions lruwap \
  --account-name $sa_name \
  --services b \
  --resource-types sco \
  --expiry $end \
  -o tsv
```

Your SAS Token is generated:

`se=2021-06-10T14%3A06Z&sp=rwlaup&sv=2018-03-28&ss=b&srt=sco&sig=OPSbZ/sJDBG3NY1MV1NAJOKR9MXIh3gKaIrTCNVXygY%3D`

```sh
export sastoken="se=2021-06-10T14%3A06Z&sp=rwlaup&sv=2018-03-28&ss=b&srt=sco&sig=OPSbZ/sJDBG3NY1MV1NAJOKR9MXIh3gKaIrTCNVXygY%3D"
```

Copy the SAS token generated and copy it into the key vault

```sh
az keyvault secret set --vault-name $keyvault_name --name "storagerw" --value $sastoken
```

```sh
#Let us gather some variable
# tenantId=$(az account list | jq '.[].tenantId')
# userId=$(az ad user list --filter "startswith(displayName, 'Barthelemy Diomaye NGOM')" | jq '.[].objectId')
# subscriptionId=$(az account subscription list | jq '.[].subscriptionId')
```

List your secrets

```sh
az keyvault secret list --vault-name $keyvault_name --output table
```

**Configure Databricks CLI**


Configure your cli to interact with databricks. You will need to enter the uri and the token generated

```sh
databricks configure --token
```

**Create a cluster in databricks**

```sh
rm -f create-cluster.json
cat <<EOF >> create-cluster.json
{
  "num_workers": null,
  "autoscale": {
      "min_workers": 2,
      "max_workers": 8
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
  "autotermination_minutes": 30,
  "cluster_source": "UI",
  "init_scripts": []
}
EOF

databricks clusters create --json-file create-cluster.json
# cluster_id=0603-150336-yuck781
# az keyvault secret set --vault-name $keyvault_name --name "cluster_id" --value $cluster_id
# Get my key vault id to be used as reference in my arm template parameter's file
#`az keyvault list | jq '.[].id'

```

**Create an Azure Key Vault-backed secret scope in Databricks**

Get the resource ID and the DNS name from your key vault properties and create a secret scope in Azure Databricks.

```sh
vaultUri=$(az keyvault show --name $keyvault_name | jq '.properties.vaultUri')
vaultId=$(az keyvault show --name $keyvault_name | jq '.id')
databricks secrets create-scope --scope demo --scope-backend-type AZURE_KEYVAULT --resource-id $vaultId --dns-name $vaultUri
```
> If the above command raise an erro, you can still create the scope from the databricks workspace using the following url https://<databricks-instance>#secrets/createScope.

![](./assets/create-scope.png)

**Release Pipeline: continue**

Let's go back to our release pipeline and finish the configuration.


## Resources

https://docs.python.org/fr/3/distributing/index.html
https://github.com/Azure-Samples/azure-sdk-for-python-storage-blob-upload-download
https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python-legacy
https://stackoverflow.com/questions/53217767/py4j-protocol-py4jerror-org-apache-spark-api-python-pythonutils-getencryptionen
https://docs.microsoft.com/fr-fr/azure/azure-resource-manager/templates/template-tutorial-use-key-vault
https://build5nines.com/azure-cli-2-0-generate-sas-token-for-blob-in-azure-storage/
https://docs.microsoft.com/fr-fr/azure/databricks/scenarios/store-secrets-azure-key-vault

