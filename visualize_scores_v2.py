# Scored durakları haritada uygunluk puanına göre renklendirme

import pandas as pd
import folium
import os
from branca.colormap import linear

# Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = os.path.join(folder_path, "scored_solar_stops.csv")
output_file = os.path.join(folder_path, "scored_stops_map.html")

# Veriyi yükle
df = pd.read_csv(input_file)

# Harita oluştur
map_center = [52.5200, 13.4050]  # Berlin
m = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')

# Renk skalası: yeşil (uygun) → kırmızı (az uygun)
colormap = linear.YlGnBu_09.scale(df['suitability_score'].min(), df['suitability_score'].max())
colormap.caption = 'Uygunluk Skoru'

# Noktaları haritaya ekle
for _, row in df.iterrows():
    lat = row['stop_lat']
    lon = row['stop_lon']
    score = row['suitability_score']
    name = row['stop_name']

    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=colormap(score),
        fill=True,
        fill_color=colormap(score),
        fill_opacity=0.8,
        popup=f"{name}<br>Skor: {score:.2f}"
    ).add_to(m)

# Renk barını haritaya ekle
colormap.add_to(m)

# Haritayı kaydet
m.save(output_file)
print(f"Skor bazlı harita oluşturuldu: {output_file}") 