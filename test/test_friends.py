import unittest
# import pyspark
import logging
from friends import friends as f
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, StructField

# from azure.storage.blob import BlockBlobService


class TestClass(unittest.TestCase):

    def setUp(self):
        """Suppress spark logging for the test context."""
        logger = logging.getLogger('py4j')
        logger.setLevel(logging.ERROR)
        self.spark = SparkSession.builder.getOrCreate()
        self.f_obj = f.Friends(self.spark, "./data/friends.csv")

    def tearDown(self):
        self.spark.stop()

    def test_load(self):
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


if __name__ == '__main__':
    unittest.main()
