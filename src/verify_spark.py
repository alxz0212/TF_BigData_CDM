from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Verify").getOrCreate()
print("Spark Version:", spark.version)
data = [("Alice", 1), ("Bob", 2)]
df = spark.createDataFrame(data, ["Name", "Value"])
df.show()
print("Verification Successful!")
spark.stop()
