# Databricks notebook source
dbutils.secrets.listScopes()

# COMMAND ----------

dbutils.secrets.list("demo")

# COMMAND ----------

print(dbutils.secrets.get(scope="demo", key="storagerw"))

# COMMAND ----------

# Unmount directory if previously mounted.
MOUNTPOINT = "/mnt/commonfiles"
if MOUNTPOINT in [mnt.mountPoint for mnt in dbutils.fs.mounts()]:
  dbutils.fs.unmount(MOUNTPOINT)

# Add the Storage Account, Container, and reference the secret to pass the SAS Token
STORAGE_ACCOUNT = dbutils.secrets.get(scope="demo", key="storageaccount")
CONTAINER = dbutils.secrets.get(scope="demo", key="container")
SASTOKEN = dbutils.secrets.get(scope="demo", key="storagerw")
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

display(dbutils.fs.ls(MOUNTPOINT))

# COMMAND ----------

friendsDF = (spark.read
              .option("header", True)
              .option("inferSchema", True)
              .csv(MOUNTPOINT + "/friends.csv"))

display(friendsDF)
# Databricks notebook source
dbutils.secrets.listScopes()

# COMMAND ----------

dbutils.secrets.list("demo")

# COMMAND ----------

print(dbutils.secrets.get(scope="demo", key="storagerw"))

# COMMAND ----------

# Unmount directory if previously mounted.
MOUNTPOINT = "/mnt/commonfiles"
if MOUNTPOINT in [mnt.mountPoint for mnt in dbutils.fs.mounts()]:
  dbutils.fs.unmount(MOUNTPOINT)

# Add the Storage Account, Container, and reference the secret to pass the SAS Token
STORAGE_ACCOUNT = dbutils.secrets.get(scope="demo", key="storageaccount")
CONTAINER = dbutils.secrets.get(scope="demo", key="container")
SASTOKEN = dbutils.secrets.get(scope="demo", key="storagerw")
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

display(dbutils.fs.ls(MOUNTPOINT))

# COMMAND ----------

friendsDF = (spark.read
              .option("header", True)
              .option("inferSchema", True)
              .csv(MOUNTPOINT + "/friends.csv"))

display(friendsDF)
