import pandas as pd
import sqlalchemy
import pymysql
from datetime import datetime

from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, \
    confusion_matrix
from sklearn.model_selection import train_test_split

# Connect to MySQL database
engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost/hartalandu_db')

# Read CSV data, assuming "date" is the first column
df_csv = pd.read_csv('progres_done.csv')

# Create empty list to store all data
all_data = []
new_df = pd.DataFrame(columns=['transactions', 'index'])

sql = f"""
SELECT *
FROM hartalandu_db.hartalandu_table5"""

# Fetch transaction data from MySQL
df_mysql = pd.read_sql_query(sql, engine)
print("date fucker", df_mysql)

# Loop through each row in the CSV
for index, row in df_csv.head(10).iterrows():
#     # Extract date from the first column
    date = datetime.strptime(row[0], '%m/%d/%Y').date()

    # date = datetime.strptime("2021-09-06", '%Y-%m-%d').date()
    filtered_df  = df_mysql.loc[df_mysql['Date'] == date]

    print(f'my df seql  is  {filtered_df}')
    combined_data = [{**filtered_df.loc[idx].to_dict()} for idx in filtered_df.index]
    print('cmb',combined_data)
    # Get latest_index on this date from the CSV
    latest_index = row['Next Close']
    print(f'latest index{latest_index}')

    # Combine features and target into a single DataFrame
    new_df.loc[index, ['transactions', 'index']] = combined_data, latest_index

X = new_df[['transactions']]
y = new_df['index']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the Linear Regression model
model = LinearRegression()

# Train the model on the training data
model.fit(X_train, y_train)

# Make predictions on the testing data
y_pred = model.predict(X_test)


# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

# Calculate precision, recall, and F1-score
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# Calculate confusion matrix
confusion = confusion_matrix(y_test, y_pred)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("Confusion Matrix:\n", confusion)

# Use y_val_labels and y_pred_labels for classification report
class_report = classification_report(y_test, y_pred)
print("Classification Report:")
print(class_report)

model.save("my_model.h5")