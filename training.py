import pandas as pd
import sqlalchemy
import numpy as np
import pymysql
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, \
    confusion_matrix
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential

# Connect to MySQL database
engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost/hartalpittal')

# Read CSV data, assuming "date" is the first column
df_csv = pd.read_csv('progres_done.csv')

# Create empty list to store all data
all_data = []
new_df = pd.DataFrame(columns=['transactions', 'index'])

sql = f"""
SELECT *
FROM hartalandu_table5
WHERE Date < '2021-09-20' """

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


def vectorize_dict_features(data, max_length=100):
    """
    Vectorize dictionary-like features into numerical arrays, padding or truncating to a fixed length.

    Args:
    data (list): List of dictionaries containing the features.
    max_length (int): Maximum length to pad or truncate the arrays. If None, use the length of the longest array.

    Returns:
    numpy.ndarray: Padded or truncated numerical array.
    """
    # Initialize an empty list to store vectorized features
    vectorized_features = []

    # Determine the maximum length if not provided
    if max_length is None:
        max_length = max(len(d.get('value', [])) for d in data)

    # Iterate over each dictionary in the list
    for d in data:
        # Here, you need to decide how to vectorize each dictionary.
        # You might convert each dictionary into a numerical array
        # based on its keys and values.
        # For demonstration, let's assume we are interested in just one key 'value'
        # and we want to extract its corresponding value for each dictionary.
        # You'll need to adapt this based on your actual data structure.
        if 'value' in d:
            # Pad or truncate the numerical array to the fixed length
            numerical_array = np.array(d['value'])
            if len(numerical_array) < max_length:
                pad_width = [(0, max_length - len(numerical_array))]
                numerical_array = np.pad(numerical_array, pad_width, mode='constant')
            elif len(numerical_array) > max_length:
                numerical_array = numerical_array[:max_length]
            vectorized_features.append(numerical_array)
        else:
            # If the key 'value' is not found, you might handle it differently,
            # such as by assigning a default value or skipping the dictionary.
            vectorized_features.append(np.zeros(max_length))  # For example, you might append zeros as a default value

    # Convert the list of vectorized features into a numpy array
    vectorized_features = np.array(vectorized_features)

    return vectorized_features
# Vectorize the 'transaction' feature in new_df
X = vectorize_dict_features(new_df['transactions'])
y = new_df['index']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = X_train
X_test_scaled = X_test

# Define your model architecture
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(1)  # Output layer for regression
])

# Compile the model with appropriate loss function for regression
model.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model.fit(X_train_scaled, y_train, epochs=10, batch_size=32, validation_split=0.1)

# Make predictions
y_pred = model.predict(X_test_scaled)

# Calculate regression metrics
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'Mean Absolute Error: {mae}')
print(f'R-squared: {r2}')



model.save("my_model.h5")