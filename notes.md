
# Data
- SNR
- NF
- BSS [ Near, Mid, Far ]
- Channel Load
- RSSI
- Frequency
- SSID
- Channel Utilisation ``[Busy, Active, Transmit] - Time``
- Station Count

# Calculating Interference

Channel load = ( Busy Time + Transmit Time / Active Time ) * 100 

SNR = RSSI - NF ``( Great is good , Less is bad )``

interference = Channel_load * BSS / max(SNR)  
