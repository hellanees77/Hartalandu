import pandas as pd
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler

# Create a SparkSession with built-in Hadoop classes
spark = SparkSession.builder \
    .appName("LinearRegressionExample") \
    .config("spark.executor.extraLibraryPath", "/Users/ranjandhungana/Downloads/hadoop-3.3.6/lib/native") \
    .config("spark.hadoop.fs.defaultFS", "file:///") \
    .config("spark.jars", "jdbc.jar") \
 \
    .getOrCreate()

# Read CSV data into a Spark DataFrame
df_csv = spark.read.csv('progres_done.csv', header=True, inferSchema=True)

# Read MySQL data into a Spark DataFrame
df_mysql = spark.read.format("jdbc").options(
    url="jdbc:mysql://localhost/hartalandu_db",
    driver="com.mysql.cj.jdbc.Driver",
    dbtable="hartalandu_table5",
    user="root",
    password="").load()

# Ensure the date column is in the correct format
df_csv = df_csv.withColumn("date", df_csv["date"].cast("date"))

# Join the two DataFrames on the date column
combined_df = df_csv.join(df_mysql, df_csv.date == df_mysql.Date)

# Define the feature columns and the target column
feature_cols = df_mysql.columns
feature_cols.remove("Date")
target_col = "Next Close"

# Assemble the feature vector
assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features")

assembled_df = assembler.transform(combined_df)

# Select features and target
data = assembled_df.select("features", target_col)

# Split the data into training and testing sets (80% train, 20% test)
train_data, test_data = data.randomSplit([0.8, 0.2], seed=123)

# Initialize the Linear Regression model
lr = LinearRegression(labelCol=target_col, featuresCol="features")

# Train the model on the training data
model = lr.fit(train_data)

# Make predictions on the testing data
predictions = model.transform(test_data)

# Evaluate the model
evaluator = RegressionEvaluator(labelCol=target_col, predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)

print("Root Mean Squared Error (RMSE) on test data = %g" % rmse)

# Save the model
model.save("my_model")

# Stop the SparkSession
spark.stop()
