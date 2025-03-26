import pandas as pd
import numpy as np
import tensorflow as tf
from keras import layers, models, optimizers

# Load dataset
df = pd.read_csv('/home/big_daddy/imoff/dataset/wifi_data.csv')

# Select features & target
feature_cols = ['Frequency', 'RSSI', 'SNR', 'BSS', 'NF', 'Ch_load']
target_col = 'Interference'

for col in feature_cols:
    if col not in df.columns:
        raise ValueError(f"Column {col} not found in dataset!")

# Handle missing values
df.fillna(df.median(), inplace=True)

X = df[feature_cols].to_numpy().astype(np.float32)

# Define TensorFlow preprocessing layers
normalizer = layers.Normalization(axis=-1)
normalizer.adapt(X)

# Split dataset
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, df[target_col], test_size=0.2, random_state=42)

# Convert to NumPy arrays
X_train, X_test = np.array(X_train), np.array(X_test)
y_train, y_test = np.array(y_train), np.array(y_test)

# Define the DNN model
model = models.Sequential([
    normalizer,  # Built-in feature scaling
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dense(16, activation='relu'),
    layers.Dense(1)  # Predicts interference
])

# Compile model
model.compile(optimizer=optimizers.Adam(learning_rate=0.001), loss=tf.keras.losses.Huber(), metrics=['mae'])

# Train model with early stopping
callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test), callbacks=[callback])

# Save the model
model.save('/home/big_daddy/imoff/models/interference_model.keras')

# Convert to TFLite for deployment
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('/home/big_daddy/imoff/models/interference_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("✅ Model trained & saved as 'interference_model.tflite'!")

# Function to predict & recommend the best channel
def recommend_best_channel(new_data):
    new_data = np.array(new_data[feature_cols])
    new_data = np.expand_dims(new_data, axis=0).astype(np.float32)  # Reshape for TFLite

    interpreter = tf.lite.Interpreter(model_path='/home/big_daddy/imoff/models/interference_model.tflite')
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], new_data)
    interpreter.invoke()
    
    interference_score = interpreter.get_tensor(output_details[0]['index'])[0][0]
    return interference_score

# Load new WiFi scan data (replace with real data)
new_data = pd.read_csv('/home/big_daddy/imoff/dataset/new_wifi_data.csv')

# Predict interference for each channel
new_data['Predicted Interference'] = new_data.apply(recommend_best_channel, axis=1)  # ✅ Fix: Pass row directly

# Recommend the best channel
best_channel = new_data.loc[new_data['Predicted Interference'].idxmin()]
print(f"✅ Recommended Channel: {best_channel['Channel']} ({best_channel['Frequency']} MHz) with Interference = {best_channel['Predicted Interference']:.2f}")

# Save results
new_data.to_csv('/home/big_daddy/imoff/dataset/predicted_wifi_data.csv', index=False)
