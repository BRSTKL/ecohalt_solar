import pandas as pd
import folium
import os
import webbrowser
from branca.colormap import linear

# Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = os.path.join(folder_path, "scored_solar_stops.csv")
output_file = os.path.join(folder_path, "scored_stops_map.html")

# Veriyi oku
df = pd.read_csv(input_file)

# Harita merkezi: Berlin
map_center = [52.5200, 13.4050]
map_berlin = folium.Map(location=map_center, zoom_start=8, tiles='OpenStreetMap')

# Renk skalası (yeşil - sarı - kırmızı)
min_score = df['suitability_score'].min()
max_score = df['suitability_score'].max()
colormap = linear.YlOrRd_09.scale(min_score, max_score)
colormap.caption = 'Uygunluk Puanı'

# Durakları haritaya ekle
for _, row in df.iterrows():
    score = row['suitability_score']
    popup_text = f"""
    <b>{row['stop_name']}</b><br>
    Güneşlenme: {row['irradiation_kWh']:.1f} kWh/yıl<br>
    Metro: {'Evet' if row['is_metro'] == 1 else 'Hayır'}<br>
    Merkez: {'Evet' if row['is_zentrum'] == 1 else 'Hayır'}<br>
    Uygunluk Puanı: {score:.3f}
    """
    
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=8,
        color=colormap(score),
        fill=True,
        fill_color=colormap(score),
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(map_berlin)

# Renk skalasını haritaya ekle
colormap.add_to(map_berlin)

# Haritayı kaydet
map_berlin.save(output_file)
print(f"Harita kaydedildi: {output_file}")
webbrowser.open(output_file) 