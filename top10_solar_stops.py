# En uygun 10 durağı belirleme algoritması
# Kriter: irradiation_kWh değeri (güneşlenme potansiyeli)

import pandas as pd
import os

# Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = os.path.join(folder_path, "stops_with_irradiation.csv")
output_file = os.path.join(folder_path, "top10_solar_stops.csv")

# Veriyi yükle
df = pd.read_csv(input_file)

# Geçerli irradiation verisi olanları filtrele
df = df[pd.notnull(df['irradiation_kWh'])]
df['irradiation_kWh'] = pd.to_numeric(df['irradiation_kWh'], errors='coerce')

# En yüksek 10 güneşlenme potansiyelli durağı seç
sorted_df = df.sort_values(by='irradiation_kWh', ascending=False)
top10 = sorted_df.head(10)

# Seçilen veriyi kaydet
top10.to_csv(output_file, index=False)

# Bilgilendir
print("En uygun 10 durak:")
print(top10[['stop_name', 'stop_lat', 'stop_lon', 'irradiation_kWh']])
print(f"\nTop 10 güneşlenmeli duraklar kaydedildi: {output_file}") 