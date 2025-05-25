import requests
import pandas as pd
import time
import os

def get_solar_irradiation(lat, lon):
    """
    PVGIS API üzerinden yıllık GHI (Global Horizontal Irradiation) verisini çek
    """
    url = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
    params = {
        "lat": lat,
        "lon": lon,
        "peakpower": 1,
        "loss": 0,
        "outputformat": "json",
        "browser": 1,
        "angle": 35,  # sabit panel açısı örnek olarak
        "optimalangles": 0,
        "raddatabase": "PVGIS-SARAH2",
        "usehorizon": 1,
        "components": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        annual_irradiation = data["outputs"]["totals"]['fixed']['E_y']  # kWh/yıl
        return annual_irradiation
    except Exception as e:
        print(f"Hata ({lat}, {lon}): {str(e)}")
        return None

def process_stops_with_solar_data(input_file, output_file, sample_size=10):
    """
    Durak verilerini oku ve güneşlenme verilerini ekle
    """
    print(f"Durak verisi okunuyor: {input_file}")
    df = pd.read_csv(input_file)
    
    # İlk N durak için güneşlenme verisi çek
    print(f"İlk {sample_size} durak için güneşlenme verisi alınıyor...")
    solar_values = []
    
    for i, row in df.head(sample_size).iterrows():
        lat = row['stop_lat']
        lon = row['stop_lon']
        print(f"Durak {i+1}/{sample_size}: {row['stop_name']} ({lat}, {lon})")
        
        irradiation = get_solar_irradiation(lat, lon)
        solar_values.append(irradiation)
        
        # API aşımını önlemek için gecikme
        time.sleep(1.5)
    
    # Veriye sütun olarak ekle
    df.loc[:sample_size-1, 'irradiation_kWh'] = solar_values
    
    # Sonuçları CSV'ye yaz
    df.to_csv(output_file, index=False)
    print(f"\nGüneşlenme verili durak dosyası kaydedildi: {output_file}")
    
    return df

if __name__ == "__main__":
    # Dosya yolları
    folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
    input_file = os.path.join(folder_path, "stops.txt")
    output_file = os.path.join(folder_path, "stops_with_irradiation.csv")
    
    # İşlemi başlat
    df = process_stops_with_solar_data(input_file, output_file, sample_size=10)
    
    # Sonuçları göster
    print("\nİlk 5 durak için güneşlenme verileri:")
    print(df[['stop_name', 'stop_lat', 'stop_lon', 'irradiation_kWh']].head()) 