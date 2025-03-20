import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib  # To save the scaler

# Step 1: Load the data from CSV file
df = pd.read_csv('channel_data_with_interference.csv')

# Step 2: Handle infinite values in 'Interference' column
df['Interference'] = pd.to_numeric(df['Interference'], errors='coerce')
df['Interference'].fillna(df['Interference'].median(), inplace=True)

# Step 3: Apply a combined log + square root transformation to the target ('Interference')
df['Interference'] = np.sqrt(np.log1p(df['Interference']))  # log(1 + Interference) and sqrt

# Step 4: Split the data into features (X) and target (y)
X = df.drop(columns=['Interference'])
y = df['Interference']

# Step 5: Normalize the features using StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Fit the scaler on training data

# Save the scaler for features (X)
joblib.dump(scaler, 'scaler.pkl')

# Normalize the target variable using MinMaxScaler after log + sqrt transformation
y_scaler = MinMaxScaler()
y_scaled = y_scaler.fit_transform(y.values.reshape(-1, 1)).flatten()

# Save the scaler for target (y)
joblib.dump(y_scaler, 'y_scaler.pkl')

# Step 6: Split the data into training and test sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

# Step 7: Build a more complex neural network model using Keras
model = models.Sequential([
    layers.Dense(128, activation='relu', input_dim=X_train.shape[1], kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    layers.Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    layers.Dense(1)  # For regression (predicting continuous values)
])

# Step 8: Compile the model with a lower learning rate and Adam optimizer
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), 
              loss='mean_squared_error', 
              metrics=['mae'])

# Step 9: Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# Step 10: Evaluate the model on the test set
test_loss, test_mae = model.evaluate(X_test, y_test)
print(f"Test Mean Absolute Error: {test_mae}")

# Save the model
model.save('interference_model.h5')
