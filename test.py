import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

# Load the model from the saved .h5 file
loaded_model = tf.keras.models.load_model('interference_model.h5')

# Load the scalers (assumed you've saved them using joblib)
scaler = joblib.load('scaler.pkl')  # Load the scaler for features
y_scaler = joblib.load('y_scaler.pkl')  # Load the scaler for target

# New data to test the model with
new_data = pd.DataFrame({
'Frequency':[2412],
'Channel':[1],
'BSS':[1],
'minsnr':[20],
'maxsnr':[45],
'NF':[-10],
'Ch_load':[23],
'spect_load':[0],
'sec_chan':[0],
'SR_bss':[0],
'SR_load':[0],
'Ch_avil':[100],
'Chan_eff':[0],
'NearBSS':[0],
'Med_BSS':[0],
'Far_BSS':[0],
'Eff_BSS':[0],
'grade':[100],
'Rank':[0],
'Unused':[0],
'Radar':[0],
})

# Scale the new data
new_data_scaled = scaler.transform(new_data)

# Make prediction using the loaded model
prediction_scaled = loaded_model.predict(new_data_scaled)

# Reverse the scaling for the prediction
prediction = y_scaler.inverse_transform(prediction_scaled)

# Print the prediction for the new data
print(f"Predicted Interference for new data: {prediction[0][0]}")
