# Scored durakları haritada uygunluk puanına göre renklendirme (Gelişmiş versiyon)

import pandas as pd
import folium
import os
from branca.colormap import linear
from folium.plugins import MarkerCluster, Fullscreen

# Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = os.path.join(folder_path, "scored_solar_stops.csv")
output_file = os.path.join(folder_path, "scored_stops_map_advanced.html")

# Veriyi yükle
df = pd.read_csv(input_file)

# Harita oluştur
map_center = [52.5200, 13.4050]  # Berlin
m = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')

# Tam ekran kontrolü ekle
Fullscreen().add_to(m)

# Marker cluster ekle
marker_cluster = MarkerCluster().add_to(m)

# Renk skalası: yeşil (uygun) → mavi (az uygun)
colormap = linear.YlGnBu_09.scale(df['suitability_score'].min(), df['suitability_score'].max())
colormap.caption = 'Uygunluk Skoru'

# Noktaları haritaya ekle
for _, row in df.iterrows():
    lat = row['stop_lat']
    lon = row['stop_lon']
    score = row['suitability_score']
    name = row['stop_name']
    irradiation = row['irradiation_kWh']
    is_metro = row['is_metro']
    is_zentrum = row['is_zentrum']

    # Detaylı popup içeriği
    popup_text = f"""
    <div style='font-family: Arial; font-size: 12px;'>
        <h4 style='margin: 0 0 5px 0;'>{name}</h4>
        <hr style='margin: 5px 0;'>
        <b>Uygunluk Skoru:</b> {score:.3f}<br>
        <b>Güneşlenme:</b> {irradiation:.1f} kWh/yıl<br>
        <b>Metro:</b> {'✓' if is_metro == 1 else '✗'}<br>
        <b>Merkez:</b> {'✓' if is_zentrum == 1 else '✗'}<br>
        <hr style='margin: 5px 0;'>
        <small>Koordinatlar: {lat:.6f}, {lon:.6f}</small>
    </div>
    """

    # Nokta boyutunu skora göre ayarla (5-10 arası)
    radius = 5 + (score * 5)

    # Marker oluştur
    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=colormap(score),
        fill=True,
        fill_color=colormap(score),
        fill_opacity=0.8,
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"{name} (Skor: {score:.2f})"
    ).add_to(marker_cluster)

# En yüksek skorlu 3 durak arasında çizgiler çiz
top3 = df.nlargest(3, 'suitability_score')
for i in range(len(top3)):
    for j in range(i+1, len(top3)):
        folium.PolyLine(
            locations=[
                [top3.iloc[i]['stop_lat'], top3.iloc[i]['stop_lon']],
                [top3.iloc[j]['stop_lat'], top3.iloc[j]['stop_lon']]
            ],
            color='red',
            weight=2,
            opacity=0.8,
            popup=f"En yüksek skorlu duraklar arası bağlantı"
        ).add_to(m)

# Renk barını haritaya ekle
colormap.add_to(m)

# Haritayı kaydet
m.save(output_file)
print(f"Gelişmiş skor bazlı harita oluşturuldu: {output_file}") 