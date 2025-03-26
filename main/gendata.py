import re
import csv
from collections import defaultdict

# File paths
wifi_scan_file = "/home/big_daddy/imoff/data/data2.txt"
survey_data_file = "/home/big_daddy/imoff/data/sdata.txt"
output_file = "/home/big_daddy/imoff/dataset/new_wifi_data.csv"

# Regex patterns for different frequency formats
wifi_freq_pattern = re.compile(r"freq:\s*(\d+\.\d+)")
survey_freq_pattern = re.compile(r"frequency:\s*(\d+)\s*MHz")

signal_pattern = re.compile(r"signal:\s*(-?\d+\.\d+)")
ssid_pattern = re.compile(r"SSID:\s*(.+)")
channel_pattern = re.compile(r"\* primary channel:\s*(\d+)")
noise_pattern = re.compile(r"noise:\s*(-?\d+)")
busy_pattern = re.compile(r"channel busy time:\s*(\d+)")
active_pattern = re.compile(r"channel active time:\s*(\d+)")
transmit_pattern = re.compile(r"channel transmit time:\s*(\d+)")

# Parse WiFi scan data (data2.txt) - Store multiple SSIDs per frequency
wifi_data = defaultdict(list)

with open(wifi_scan_file, "r") as file:
    current_entry = {"Frequency": None, "RSSI": None, "Channel": None, "SSID": None}
    for line in file:
        freq_match = wifi_freq_pattern.search(line)
        signal_match = signal_pattern.search(line)
        ssid_match = ssid_pattern.search(line)
        channel_match = channel_pattern.search(line)

        if freq_match:
            if current_entry["Frequency"]:  
                wifi_data[current_entry["Frequency"]].append(current_entry)  # Save the last AP before starting a new one
            current_entry = {"Frequency": int(float(freq_match.group(1))), "RSSI": None, "Channel": None, "SSID": None}

        if signal_match:
            current_entry["RSSI"] = float(signal_match.group(1))

        if ssid_match:
            ssid = ssid_match.group(1).strip()
            if current_entry["SSID"]:  
                # If SSID already exists, create a new entry for this frequency
                wifi_data[current_entry["Frequency"]].append(current_entry.copy())
                current_entry["RSSI"] = None  # Reset RSSI for new SSID
            current_entry["SSID"] = ssid

        if channel_match:
            current_entry["Channel"] = int(channel_match.group(1))

    if current_entry["Frequency"]:  
        wifi_data[current_entry["Frequency"]].append(current_entry)  # Save last entry

# Calculate BSS (Number of SSIDs per Frequency)
bss_count = {freq: len(wifi_data[freq]) for freq in wifi_data}  # Count SSIDs at each frequency

for freq in wifi_data:
    for entry in wifi_data[freq]:
        entry["BSS"] = bss_count[freq]  # Assign BSS count to all SSIDs at the same frequency

# Parse survey data (sdata.txt) - Keep unique frequency records
survey_data = {}
with open(survey_data_file, "r") as file:
    current_freq = None
    for line in file:
        freq_match = survey_freq_pattern.search(line)
        noise_match = noise_pattern.search(line)
        busy_match = busy_pattern.search(line)
        active_match = active_pattern.search(line)
        transmit_match = transmit_pattern.search(line)

        if freq_match:
            current_freq = int(freq_match.group(1))
            if current_freq not in survey_data:
                survey_data[current_freq] = {"Frequency": current_freq, "NF": None, "Channel Load": 0}

        if noise_match:
            survey_data[current_freq]["NF"] = int(noise_match.group(1))

        if busy_match:
            survey_data[current_freq]["Busy"] = int(busy_match.group(1))

        if active_match:
            survey_data[current_freq]["Active"] = int(active_match.group(1))

        if transmit_match:
            survey_data[current_freq]["Transmit"] = int(transmit_match.group(1))

# Merge datasets - Keep multiple SSIDs per frequency
final_data = []
for freq in wifi_data:
    if freq in survey_data:
        for entry in wifi_data[freq]:
            rssi = entry.get("RSSI", None)
            nf = survey_data[freq].get("NF", None)
            channel_load = ((survey_data[freq].get("Busy", 0) + survey_data[freq].get("Transmit", 0)) / survey_data[freq].get("Active", 0) * 100) if survey_data[freq].get("Active", 0) > 0 else 0

            bss = entry.get("BSS", 0)

            # Compute SNR & Interference
            snr = (rssi - nf) if (rssi is not None and nf is not None) else None
            interference = (channel_load * bss) / max(snr, 1) if snr is not None else None

            final_data.append({
                "Frequency": freq,
                "RSSI": rssi,
                "SNR": snr,
                "Channel": entry.get("Channel", None),
                "BSS": bss,
                "NF": nf,
                "Ch_load": channel_load,
                "Interference": interference
            })

# Save to CSV
with open(output_file, "w", newline="") as csvfile:
    fieldnames = ["Frequency", "RSSI", "SNR", "Channel", "BSS", "NF", "Ch_load", "Interference"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_data)

print(f"✅ WiFi data parsed and saved to {output_file}")