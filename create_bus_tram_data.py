# Otobüs ve tramvay duraklarını filtrele ve güneşlenme verilerini ekle

import pandas as pd
import os
import requests
import time

# Dosya yolları
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
stops_file = os.path.join(folder_path, "stops.txt")
output_file = os.path.join(folder_path, "bus_tram_stops_with_irradiation.csv")

# Durakları oku
df = pd.read_csv(stops_file)

# Otobüs ve tramvay duraklarını filtrele
bus_tram_stops = df[df['stop_name'].str.contains('Bus|Tram|bus|tram', na=False)].copy()

# Berlin sınırları (yaklaşık):
# Enlem: 52.3382 - 52.6755
# Boylam: 13.0883 - 13.7611
berlin_mask = (
    (bus_tram_stops['stop_lat'] >= 52.3382) & (bus_tram_stops['stop_lat'] <= 52.6755) &
    (bus_tram_stops['stop_lon'] >= 13.0883) & (bus_tram_stops['stop_lon'] <= 13.7611)
)
bus_tram_stops = bus_tram_stops[berlin_mask].copy()

def get_solar_irradiation(lat, lon):
    """PVGIS API'den yıllık toplam güneşlenme verisi al (kWh/m2/yıl)"""
    url = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
    params = {
        "lat": lat,
        "lon": lon,
        "raddatabase": "PVGIS-SARAH2",
        "components": 1,
        "outputformat": "json",
        "peakpower": 1,  # Zorunlu parametre
        "loss": 14       # Zorunlu parametre
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Yıllık toplam global irradiation (kWh/m2/yıl)
            return data['outputs']['totals']['fixed']['E_y']
        else:
            print(f"Hata: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None

# Güneşlenme verilerini ekle
print(f"Toplam {len(bus_tram_stops)} otobüs ve tramvay durağı işleniyor...")
irradiation_data = []

for idx, row in bus_tram_stops.iterrows():
    print(f"Durak {idx+1}/{len(bus_tram_stops)}: {row['stop_name']}")
    irradiation = get_solar_irradiation(row['stop_lat'], row['stop_lon'])
    irradiation_data.append(irradiation)
    time.sleep(1)  # API rate limit için bekleme

# Güneşlenme verilerini DataFrame'e ekle
bus_tram_stops['irradiation_kWh'] = irradiation_data

# Sonuçları kaydet
bus_tram_stops.to_csv(output_file, index=False)
print(f"\nVeriler kaydedildi: {output_file}")

# İstatistikler
total_stops = len(bus_tram_stops)
valid_irradiation = bus_tram_stops['irradiation_kWh'].notna().sum()
print(f"\nİstatistikler:")
print(f"Toplam durak sayısı: {total_stops}")
print(f"Güneşlenme verisi alınan durak sayısı: {valid_irradiation}")
print(f"Başarı oranı: {(valid_irradiation/total_stops)*100:.1f}%") 