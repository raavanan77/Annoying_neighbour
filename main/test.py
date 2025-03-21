import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

# Load the model from the saved .h5 file
loaded_model = tf.keras.models.load_model('/home/big_daddy/imoff/models/interference_model.h5', compile=False)

# Load the scalers
scaler = joblib.load('/home/big_daddy/imoff/models/scaler.pkl')
y_scaler = joblib.load('/home/big_daddy/imoff/models/y_scaler.pkl')

# Define a function to handle predictions
def make_prediction(new_data):
    # Scale new data
    new_data_scaled = scaler.transform(new_data)

    # Ensure the input has at least 'time_steps' entries (e.g., 10 past readings)
    time_steps = 10  # Must match training

    # If new_data has fewer than `time_steps`, pad it with zeros
    if new_data_scaled.shape[0] < time_steps:
        padding = np.zeros((time_steps - new_data_scaled.shape[0], new_data_scaled.shape[1]))
        new_data_scaled = np.vstack([new_data_scaled, padding])

    # Reshape to (1, time_steps, num_features) for LSTM
    new_data_3D = new_data_scaled.reshape(1, time_steps, -1)

    # Make prediction
    prediction_scaled = loaded_model.predict(new_data_3D)

    # Reverse the scaling
    prediction = y_scaler.inverse_transform(prediction_scaled.reshape(-1, 1))

    return prediction[0][0]


new_data_case5 = pd.DataFrame({
    'Frequency': [2422],
    'SNR': [-10],
    'RSSI': [-80],
    'Neighbours': [13],
    'Ch_load': [100],
})

prediction_case5 = make_prediction(new_data_case5)
print(f"Case 5 - Predicted Interference: {prediction_case5}")
