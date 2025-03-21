import pandas as pd

# Load the CSV
df = pd.read_csv("/home/big_daddy/imoff/dataset/channel_data_with_interference.csv")

# Preview data
print(df.head())

import seaborn as sns
import matplotlib.pyplot as plt

# Create pivot table for heatmap
heatmap_data = df.pivot(index="Frequency", columns="Ch_load", values="Interference")

# Plot heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".2f")
plt.title("WiFi Channel Interference Heatmap")
plt.show()
