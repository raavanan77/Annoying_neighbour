import csv
import re

def parser(text):
    noise = re.compile(r"noise:\s*(-?\d+) dBm")
    rssi = re.compile(r"signal:\s*(-?\d+\.\d+) dBm")
    nfreq = re.compile(r"frequency:\s+(\d+)\s+MHz")
    freq = re.compile(r"freq:\s*(\d+\.\d+)")
    ssid = re.compile(r"SSID:\s*(\S+)")
    cat = re.compile(r"channel\s+active\s+time:\s*(\d+) ms\s")
    cbt = re.compile(r"channel\s+busy\s+time:\s*(\d+) ms\s")
    ctt = re.compile(r"channel\s+transmit\s+time:\s*(\d+) ms")
    stac = re.compile(r"station\s+count:\s*(\d+)")
    bss = re.compile(r"BSS\s+([A-Za-z0-9]+(:[A-Za-z0-9]+)+)")

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

    FREQ = list({int(float(x)) for x in FREQ})
    NFREQ = list(set(NFREQ))
    SSID, RSSI = list(set(SSID)), list(set(RSSI))
    Channl_load = [((int(y)+int(z)) / (int(x) + 1e-16)) * 100 for x,y,z in zip(CAT,CBT,CTT)]
    SNR = [float(x) - float(y) for x,y in zip(RSSI,NOISE)]


    with open('/home/big_daddy/imoff/dataset/channel_data_with_interference.csv', mode='w', newline='') as csv_file:
        fieldnames = ['Frequency', 'SNR', 'RSSI', 'Neighbours', 'Ch_load', 'Interference']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(FREQ)):
            for j in range(len(NFREQ)):
                print(FREQ[i], NFREQ[j], type(FREQ[i]),type(NFREQ[j]))
                if FREQ[i] == int(NFREQ[j]):
                    frequency = int(float(FREQ[i]))
                    signal = int(float(RSSI[i]))
                    Neighbour = FREQ.count(FREQ[i])
                    snr = int(float(SNR[i]))
                    writer.writerow({
                        'Frequency': frequency,
                        'SNR': snr,
                        'RSSI':signal,
                        'Neighbours':Neighbour,
                        'Ch_load': Channl_load[j],
                        'Interference': ((Channl_load[j] + Neighbour) / max(1,100 - snr)) *100
                    })
            pass    

with open('/home/big_daddy/imoff/data/data3.txt','r') as file:
    data = file.read()

parser(data)


