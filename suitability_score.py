# AI destekli uygunluk puanı hesaplama (örnek basit model)
# Kullanılan kriterler: irradiation_kWh, metro/zentrum yakınlığı gibi basit özellikler

import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler

# Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = os.path.join(folder_path, "stops_with_irradiation.csv")
output_file = os.path.join(folder_path, "scored_solar_stops.csv")

# Veriyi oku
df = pd.read_csv(input_file)

# Eksik verileri temizle
df = df[pd.notnull(df['irradiation_kWh'])]
df['irradiation_kWh'] = pd.to_numeric(df['irradiation_kWh'], errors='coerce')

# Özellik 1: Yüksek güneşlenme potansiyeli (normalize edilmiş)
scaler = MinMaxScaler()
df['irradiation_score'] = scaler.fit_transform(df[['irradiation_kWh']])

# Özellik 2: Metroya yakınlık (adı "U " ile başlayan duraklar)
df['is_metro'] = df['stop_name'].str.contains("U ", case=False, na=False).astype(int)

# Özellik 3: Zentrum içeren adlar (merkez)
df['is_zentrum'] = df['stop_name'].str.contains("Zentrum", case=False, na=False).astype(int)

# Final Skor: Basit ağırlıklı toplam (geliştirilebilir)
df['suitability_score'] = (
    0.7 * df['irradiation_score'] +
    0.2 * df['is_metro'] +
    0.1 * df['is_zentrum']
)

# Skora göre sırala ve ilk 10 durağı al
top10_scored = df.sort_values(by='suitability_score', ascending=False).head(10)

top10_scored.to_csv(output_file, index=False)

print("Uygunluk skoruna göre en iyi 10 durak:")
print(top10_scored[['stop_name', 'irradiation_kWh', 'is_metro', 'is_zentrum', 'suitability_score']])
print(f"\nSonuç kaydedildi: {output_file}") 