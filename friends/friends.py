from pyspark.sql.dataframe import DataFrame
from pyspark.sql.session import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, StructField


class Friends:

    def __init__(self, spark: SparkSession, file_path: str):
        self.spark = spark
        self.file_path = file_path

    def mount_dataset(self, path):
        return 1

    def load(self):
        friendSchema = StructType([
            StructField('id', IntegerType()),
            StructField('name', StringType()),
            StructField('age', IntegerType()),
            StructField('friends', StringType())
            ])
        return (self.spark.read
                    .format("csv")
                    .option("header", True)
                    .schema(friendSchema)
                    .load(self.file_path))

    def save_as_parquet(self, df: DataFrame, file_name: str):
        df.write.parquet(file_name)

    def create_table(self, df: DataFrame, table_name: str, file_name: str):
        parquetFile = self.spark.read.parquet(file_name)
        parquetFile.createOrReplaceTempView(table_name)
