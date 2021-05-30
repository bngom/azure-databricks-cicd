import unittest
import pyspark
import sys
from pyspark.sql import SparkSession
from src import friends as f
# from azure.storage.blob import BlockBlobService
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType, DoubleType, StructField
# from pyspark.sql import SparkSession
# from src.modules import friends as f


class TestClass(unittest.TestCase):

    def setUp(self):    
        self.spark = SparkSession.builder.getOrCreate()
        self.f_obj = f.Friends(self.spark, "data\\friends-BADFILE.csv")

    def tearDown(self):
        #self.spark.stop()
        pass

    def test_load_dataset(self):
        try:
            self.f_obj.load()
        except AssertionError as error:
            self.assertEqual(1, 0)
    
    def test_schema(self):
        schema = StructType([
            StructField('id', IntegerType()),
            StructField('name', StringType()),
            StructField('age', IntegerType()),
            StructField('friends', StringType())
            ])  
        df_schema = self.f_obj.load()
        self.assertEqual(df_schema.schema, schema)

    def test_mount_dataset(self):
        # Will be usefull to test if the blob exist in a container on azure
        pass
        
    def test_create_table(self):
        # check if dataset has header
        pass


if __name__ == '__main__':
    unittest.main()
    