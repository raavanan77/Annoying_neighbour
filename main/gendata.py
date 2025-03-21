import csv
import re

def parser(text):
    # Regular expressions
    noise = re.compile(r"noise:\s*(-?\d+) dBm")
    rssi = re.compile(r"signal:\s*(-?\d+\.\d+) dBm")
    nfreq = re.compile(r"frequency:\s+(\d+)\s+MHz")
    freq = re.compile(r"freq:\s*(\d+\.\d+)")
    ssid = re.compile(r"SSID:\s*(\S+)")
    cat = re.compile(r"channel\s+active\s+time:\s*(\d+) ms\s")
    cbt = re.compile(r"channel\s+busy\s+time:\s*(\d+) ms\s")
    ctt = re.compile(r"channel\s+transmit\s+time:\s*(\d+) ms")
    stac = re.compile(r"station\s+count:\s*(\d+)")
    bss = re.compile(r"BSS\s+([A-Za-z0-9]+(:[A-Za-z0-9]+)+)\s+\(on\s+(\S+)\)")

    # Extract data using regex
    NOISE = noise.findall(text)
    NFREQ = nfreq.findall(text)
    RSSI = rssi.findall(text)
    FREQ = freq.findall(text)
    SSID = ssid.findall(text)
    CAT = cat.findall(text)
    CBT = cbt.findall(text)
    CTT = ctt.findall(text)
    STAC = stac.findall(text)
    BSS = bss.findall(text)

    # Data transformations and cleaning
    FREQ = list({int(float(x)) for x in FREQ})
    NFREQ = list(set(NFREQ))
    SSID, RSSI = list(set(SSID)), list(set(RSSI))
    Channl_load = [((int(y) + int(z)) / (int(x) + 1e-16)) * 100 for x, y, z in zip(CAT, CBT, CTT)]
    SNR = [float(x) - float(y) for x, y in zip(RSSI, NOISE)]

    # Write data to CSV
    with open('/home/big_daddy/imoff/dataset/channel_data_with_interference.csv', mode='w', newline='') as csv_file:
        fieldnames = ['Frequency', 'SNR', 'RSSI', 'Neighbours', 'Ch_load', 'Interference']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Writing BSS and survey data to CSV
        for i, freq in enumerate(FREQ):
            for j, nf in enumerate(NFREQ):
                if freq == int(nf):
                    frequency = freq
                    signal = int(float(RSSI[i]))
                    Neighbour = FREQ.count(freq)
                    snr = int(float(SNR[i]))
                    interference = ((Channl_load[j] + Neighbour) / max(1, 100 - snr)) * 100
                    writer.writerow({
                        'Frequency': frequency,
                        'SNR': snr,
                        'RSSI': signal,
                        'Neighbours': Neighbour,
                        'Ch_load': Channl_load[j],
                        'Interference': interference
                    })

        # Optionally write BSS data to a separate CSV or log
        # If you want to track the BSS information:
        with open('/home/big_daddy/imoff/dataset/bss_data.csv', mode='w', newline='') as bss_file:
            bss_fieldnames = ['BSS', 'Frequency', 'Last Seen', 'Signal Strength']
            bss_writer = csv.DictWriter(bss_file, fieldnames=bss_fieldnames)
            bss_writer.writeheader()
            for bss_info in BSS:
                bss_writer.writerow({
                    'BSS': bss_info[0],
                    'Frequency': bss_info[2],  # Extracting frequency from the BSS information
                    'Last Seen': bss_info[1],  # Could extract more specific time info
                    'Signal Strength': RSSI[0]  # Assuming RSSI[0] matches your needs for now
                })

# Open and parse the input data
with open('/home/big_daddy/imoff/data/data3.txt', 'r') as file:
    data = file.read()

parser(data)
