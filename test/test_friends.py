import unittest
<<<<<<< HEAD
import pyspark
import logging
from src import friends as f

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType, DoubleType, StructField
=======
# import pyspark
import logging
import friends as f
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, StructField
>>>>>>> dev

# from azure.storage.blob import BlockBlobService


class TestClass(unittest.TestCase):

<<<<<<< HEAD
    def setUp(self):    
=======
    def setUp(self):
>>>>>>> dev
        """Suppress spark logging for the test context."""
        logger = logging.getLogger('py4j')
        logger.setLevel(logging.ERROR)
        self.spark = SparkSession.builder.getOrCreate()
<<<<<<< HEAD
        self.f_obj = f.Friends(self.spark, "data\\friends.csv")
=======
        self.f_obj = f.Friends(self.spark, "./data/friends.csv")
>>>>>>> dev

    def tearDown(self):
        self.spark.stop()

    def test_load(self):
<<<<<<< HEAD
        df = self.f_obj.load()
        df.show()
    
    # def test_schema(self):
    #     schema = StructType([
    #         StructField('id', IntegerType()),
    #         StructField('name', StringType()),
    #         StructField('age', IntegerType()),
    #         StructField('friends', StringType())
    #         ])  
    #     df_schema = self.f_obj.load()
    #     df_schema.printSchema
    #     self.assertTrue(df_schema.schema==schema)
=======
        self.f_obj.load()

    def test_schema(self):
        expected_schema = StructType([
            StructField('id', IntegerType()),
            StructField('name', StringType()),
            StructField('age', IntegerType()),
            StructField('friends', StringType())
            ])
        df_schema = self.f_obj.load().schema
        self.assertTrue(df_schema == expected_schema)
>>>>>>> dev


if __name__ == '__main__':
    unittest.main()
<<<<<<< HEAD
    
=======
>>>>>>> dev
