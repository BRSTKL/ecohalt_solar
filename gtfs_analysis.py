import pandas as pd
import folium
import os
import webbrowser
import numpy as np
from branca.colormap import linear

# GTFS stops.txt dosyasını oku
def read_stops_file(file_path):
    try:
        # CSV dosyasını oku (GTFS stops.txt bir CSV dosyasıdır)
        stops_df = pd.read_csv(file_path)
        print(f"Toplam {len(stops_df)} durak noktası okundu.")
        print("\nİlk 5 durak:")
        print(stops_df.head())
        return stops_df
    except FileNotFoundError:
        print(f"Hata: {file_path} dosyası bulunamadı!")
        return None
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return None

def create_stops_map(df, output_path, title="Berlin Durakları"):
    # Harita merkezi: Berlin
    map_center = [52.5200, 13.4050]
    map_berlin = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')
    
    # Tüm durakları haritaya ekle
    for _, row in df.iterrows():
        if pd.notnull(row['stop_lat']) and pd.notnull(row['stop_lon']):
            folium.CircleMarker(
                location=[row['stop_lat'], row['stop_lon']],
                radius=2,
                color='blue',
                fill=True,
                fill_opacity=0.6,
                popup=row['stop_name']  # Durak adını popup olarak göster
            ).add_to(map_berlin)
    
    # Haritayı kaydet
    map_berlin.save(output_path)
    print(f"Harita kaydedildi: {output_path}")
    
    # Haritayı otomatik aç
    webbrowser.open(output_path)

def create_colored_solar_map(df, output_path, value_col='irradiation_kWh', lat_col='stop_lat', lon_col='stop_lon', name_col='stop_name'):
    # Harita merkezi: Berlin
    map_center = [52.5200, 13.4050]
    map_berlin = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')

    # Renk skalası (sarı - turuncu - kırmızı)
    min_val = df[value_col].min()
    max_val = df[value_col].max()
    colormap = linear.YlOrRd_09.scale(min_val, max_val)
    colormap.caption = 'Yıllık Güneşlenme (kWh/yıl)'

    # Durakları haritaya ekle
    for _, row in df.iterrows():
        val = row[value_col]
        if pd.notnull(row[lat_col]) and pd.notnull(row[lon_col]) and pd.notnull(val):
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=3,
                color=colormap(val),
                fill=True,
                fill_color=colormap(val),
                fill_opacity=0.7,
                popup=f"{row[name_col]}<br>{value_col}: {val:.1f} kWh"
            ).add_to(map_berlin)

    # Renk skalasını haritaya ekle
    colormap.add_to(map_berlin)

    # Haritayı kaydet
    map_berlin.save(output_path)
    print(f"Güneşlenme renkli harita kaydedildi: {output_path}")
    webbrowser.open(output_path)

if __name__ == "__main__":
    # stops.txt dosyasının bulunduğu klasör
    folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
    file_path = os.path.join(folder_path, "stops.txt")
    
    # Dosyayı oku
    stops_data = read_stops_file(file_path)
    
    if stops_data is not None:
        # Kolon adlarını kontrol et
        print("\nKolonlar:", stops_data.columns)
        
        # Filtreleme örnekleri
        print("\nFiltreleme örnekleri:")
        
        # 1. "Zentrum" içeren duraklar
        zentrum_stops = stops_data[stops_data['stop_name'].str.contains("Zentrum", case=False, na=False)]
        print(f"\n'Zentrum' içeren durak sayısı: {len(zentrum_stops)}")
        
        # 2. Metro durakları (örnek: U-Bahn)
        metro_stops = stops_data[stops_data['stop_name'].str.contains("U ", case=False, na=False)]
        print(f"Metro (U-Bahn) durak sayısı: {len(metro_stops)}")
        
        # 3. Tramvay durakları (örnek: Tram)
        tram_stops = stops_data[stops_data['stop_name'].str.contains("Tram", case=False, na=False)]
        print(f"Tramvay durak sayısı: {len(tram_stops)}")
        
        # Filtrelenmiş durakları haritada göster
        output_path = os.path.join(folder_path, "berlin_stops_map.html")
        create_stops_map(stops_data, output_path)
        
        # Zentrum duraklarını ayrı bir haritada göster
        zentrum_output = os.path.join(folder_path, "berlin_zentrum_stops.html")
        create_stops_map(zentrum_stops, zentrum_output, "Berlin Zentrum Durakları")

    # stops_with_irradiation.csv dosyasını oku
    input_file = os.path.join(folder_path, "stops_with_irradiation.csv")
    if not os.path.exists(input_file):
        print(f"Dosya bulunamadı: {input_file}")
    else:
        df = pd.read_csv(input_file)
        # Sadece irradiation_kWh değeri olanları filtrele
        df = df[pd.notnull(df['irradiation_kWh'])]
        df['irradiation_kWh'] = pd.to_numeric(df['irradiation_kWh'], errors='coerce')
        output_path = os.path.join(folder_path, "berlin_solar_stops_map.html")
        create_colored_solar_map(df, output_path) 