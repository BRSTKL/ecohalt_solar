# Tüm Berlin otobüs ve tramvay duraklarını güneşlenme verisiyle haritada görselleştirme

import pandas as pd
import folium
import os
from branca.colormap import linear
from folium.plugins import Fullscreen

# 🔧 Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = os.path.join(folder_path, "bus_tram_stops_with_irradiation.csv")
output_file = os.path.join(folder_path, "bus_tram_solar_map.html")

# 📄 Veriyi oku
df = pd.read_csv(input_file)
df = df[pd.notnull(df['irradiation_kWh'])]

# 🗺 Harita başlat
map_center = [52.5200, 13.4050]
m = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')
Fullscreen().add_to(m)

# 🎨 Renk skalası
colormap = linear.YlOrRd_09.scale(df['irradiation_kWh'].min(), df['irradiation_kWh'].max())
colormap.caption = 'Yıllık Güneşlenme (kWh/yıl)'

# 📍 Noktaları ekle
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=4,
        color=colormap(row['irradiation_kWh']),
        fill=True,
        fill_color=colormap(row['irradiation_kWh']),
        fill_opacity=0.8,
        popup=f"{row['stop_name']}<br>Güneşlenme: {row['irradiation_kWh']:.1f} kWh"
    ).add_to(m)

# 🎚️ Renk skalası ekle
colormap.add_to(m)

# 💾 Haritayı kaydet
m.save(output_file)
print(f"Harita oluşturuldu: {output_file}") 