# Databricks notebook source
# MAGIC %md
# MAGIC # Demo CICD with Databricks and Azure DevOps

# COMMAND ----------

# MAGIC %pip list

# COMMAND ----------

# Import our library
from friends import friends as f

# COMMAND ----------

# MAGIC %md
# MAGIC ## Mount the Azure Storage Account Container

# COMMAND ----------

# Mount Azure Blob
# Unmount directory if previously mounted.
MOUNTPOINT = "/mnt/adaltas"
if MOUNTPOINT in [mnt.mountPoint for mnt in dbutils.fs.mounts()]:
  dbutils.fs.unmount(MOUNTPOINT)

# Add the Storage Account, Container, and reference the secret to pass the SAS Token
STORAGE_ACCOUNT = dbutils.secrets.get(scope="demo", key="storageaccount")
CONTAINER = dbutils.secrets.get(scope="demo", key="container")
SASTOKEN = dbutils.secrets.get(scope="demo", key="storagerw")

# Do not change these values
SOURCE = "wasbs://{container}@{storage_acct}.blob.core.windows.net/".format(container=CONTAINER, storage_acct=STORAGE_ACCOUNT)
URI = "fs.azure.sas.{container}.{storage_acct}.blob.core.windows.net".format(container=CONTAINER, storage_acct=STORAGE_ACCOUNT)

try:
  dbutils.fs.mount(
    source=SOURCE,
    mount_point=MOUNTPOINT,
    extra_configs={URI:SASTOKEN})
except Exception as e:
  if "Directory already mounted" in str(e):
    pass # Ignore error if already mounted.
  else:
    raise e

# display(dbutils.fs.ls())


# COMMAND ----------

display(dbutils.fs.ls("/mnt/adaltas/"))

# COMMAND ----------

f_obj = f.Friends(spark=spark, file_path="/mnt/adaltas")

# COMMAND ----------

df = f_obj.load()

# COMMAND ----------

df.show()

# COMMAND ----------

file_name="/tmp/friends.parquet"
dbutils.fs.rm(file_name, True)
f_obj.save_as_parquet(df=df, file_name=file_name)

# COMMAND ----------

dbutils.fs.ls(file_name)

# COMMAND ----------

f_obj.create_table(df=df, table_name="friends", file_name=file_name)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM friends LIMIT 10
