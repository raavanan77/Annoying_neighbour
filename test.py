import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

# Load the model from the saved .h5 file
loaded_model = tf.keras.models.load_model('interference_model.h5',compile=False)

# Load the scalers (assumed you've saved them using joblib)
scaler = joblib.load('scaler.pkl')  # Load the scaler for features
y_scaler = joblib.load('y_scaler.pkl')  # Load the scaler for target

# New data to test the model with
new_data = pd.DataFrame({
'Frequency':[2412],
'Channel':[1],
'BSS':[45],
'minsnr':[40],
'maxsnr':[95],
'NF':[-90],
'Ch_load':[99],
'spect_load':[0],
'sec_chan':[0],
'SR_bss':[0],
'SR_load':[0],
'Ch_avil':[100],
'Chan_eff':[0],
'NearBSS':[34],
'Med_BSS':[17],
'Far_BSS':[10],
'Eff_BSS':[0],
'grade':[100],
'Rank':[0],
'Unused':[0],
'Radar':[0],
})

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

print(f"Predicted Interference: {prediction[0][0]}")

