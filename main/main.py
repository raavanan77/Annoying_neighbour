import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

# Load data
df = pd.read_csv('/home/big_daddy/imoff/dataset/channel_data_with_interference.csv')

print(df.shape)


df['Interference'] = pd.to_numeric(df['Interference'], errors='coerce')
df['Interference'].fillna(df['Interference'].median(), inplace=True)
df['Interference'] = np.sqrt(np.log1p(df['Interference']))

# Define feature columns
target_col = 'Interference'
feature_cols = [col for col in df.columns if col != target_col]  # Auto-select all except target


# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[feature_cols])
joblib.dump(scaler, '/home/big_daddy/imoff/models/scaler.pkl')

y_scaler = MinMaxScaler()
y_scaled = y_scaler.fit_transform(df[target_col].values.reshape(-1, 1)).flatten()
joblib.dump(y_scaler, '/home/big_daddy/imoff/models/y_scaler.pkl')

# Convert to 3D (sliding window)
time_steps = 10  # Use last 10 readings
X_list, y_list = [], []
for i in range(len(X_scaled) - time_steps):
    X_list.append(X_scaled[i:i + time_steps])
    y_list.append(y_scaled[i + time_steps])

X_3D = np.array(X_list)
y_3D = np.array(y_list)

print(f"X_3D shape: {X_3D.shape}, y_3D shape: {y_3D.shape}")


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_3D, y_3D, test_size=0.2, random_state=42)

# Build LSTM model
model = models.Sequential([
    layers.LSTM(128, activation='relu', return_sequences=True, input_shape=(time_steps, X_train.shape[2])),
    layers.LSTM(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(1)
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss='mse', metrics=['mae'])

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# Evaluate
test_loss, test_mae = model.evaluate(X_test, y_test)
print(f"Test MAE: {test_mae}")

# Save model
model.save('/home/big_daddy/imoff/models/interference_model.h5')
