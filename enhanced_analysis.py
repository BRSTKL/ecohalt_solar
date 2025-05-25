import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import folium
from folium.plugins import MarkerCluster
import branca.colormap as cm

def load_and_prepare_data():
    """Verileri yükle ve hazırla"""
    # Ana veri setini yükle
    df = pd.read_csv("GTFS/bus_tram_stops_with_irradiation.csv")
    
    # Metro istasyonlarına olan uzaklık (örnek veri - gerçek veri ile değiştirilmeli)
    df['metro_distance'] = np.random.uniform(0, 2000, len(df))  # metre cinsinden
    
    # Yolcu yoğunluğu (örnek veri - gerçek veri ile değiştirilmeli)
    df['passenger_density'] = np.random.uniform(0, 100, len(df))
    
    # Bina yoğunluğu (örnek veri - gerçek veri ile değiştirilmeli)
    df['building_density'] = np.random.uniform(0, 1, len(df))
    
    # Gölgelenme faktörü (örnek veri - gerçek veri ile değiştirilmeli)
    df['shading_factor'] = np.random.uniform(0, 1, len(df))
    
    return df

def calculate_suitability_score(df):
    """Uygunluk skoru hesapla"""
    # Özellikleri normalize et
    scaler = MinMaxScaler()
    features = ['irradiation_kWh', 'metro_distance', 'passenger_density', 
                'building_density', 'shading_factor']
    
    normalized_features = pd.DataFrame(
        scaler.fit_transform(df[features]),
        columns=features
    )
    
    # Ağırlıklar (bu değerler ayarlanabilir)
    weights = {
        'irradiation_kWh': 0.4,        # Güneşlenme potansiyeli
        'metro_distance': -0.2,        # Metroya yakınlık (negatif çünkü uzaklık)
        'passenger_density': 0.2,      # Yolcu yoğunluğu
        'building_density': -0.1,      # Bina yoğunluğu (negatif çünkü gölgelenme)
        'shading_factor': -0.1         # Gölgelenme faktörü (negatif çünkü gölge)
    }
    
    # Uygunluk skorunu hesapla
    df['suitability_score'] = sum(
        normalized_features[feature] * weight 
        for feature, weight in weights.items()
    )
    
    # Skoru 0-100 arasına normalize et
    df['suitability_score'] = (
        (df['suitability_score'] - df['suitability_score'].min()) /
        (df['suitability_score'].max() - df['suitability_score'].min()) * 100
    )
    
    return df

def get_top_recommendations(df, n=10):
    """En uygun n durağı öner"""
    return df.nlargest(n, 'suitability_score')[
        ['stop_name', 'stop_lat', 'stop_lon', 'irradiation_kWh', 
         'metro_distance', 'passenger_density', 'suitability_score']
    ]

def create_enhanced_map(df, top_recommendations):
    """Gelişmiş harita oluştur"""
    # Berlin merkezi
    center_lat = df['stop_lat'].mean()
    center_lon = df['stop_lon'].mean()
    
    # Ana harita
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Renk skalası
    colormap = cm.LinearColormap(
        colors=['red', 'yellow', 'green'],
        vmin=df['suitability_score'].min(),
        vmax=df['suitability_score'].max(),
        caption='Uygunluk Skoru'
    )
    colormap.add_to(m)
    
    # Marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Tüm durakları ekle
    for idx, row in df.iterrows():
        # Popup içeriği
        popup_content = f"""
        <div style='font-family: Arial; width: 200px;'>
            <h4 style='margin-bottom: 5px;'>{row['stop_name']}</h4>
            <p style='margin: 2px 0;'>Güneşlenme: {row['irradiation_kWh']:.1f} kWh/yıl</p>
            <p style='margin: 2px 0;'>Metro Uzaklığı: {row['metro_distance']:.0f} m</p>
            <p style='margin: 2px 0;'>Yolcu Yoğunluğu: {row['passenger_density']:.1f}</p>
            <p style='margin: 2px 0;'>Uygunluk Skoru: {row['suitability_score']:.1f}</p>
        </div>
        """
        
        # Marker ekle
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=5,
            popup=folium.Popup(popup_content, max_width=300),
            color=colormap(row['suitability_score']),
            fill=True,
            fill_color=colormap(row['suitability_score']),
            fill_opacity=0.7,
            tooltip=row['stop_name']
        ).add_to(marker_cluster)
    
    # En iyi önerileri özel işaretleyici ile göster
    for idx, row in top_recommendations.iterrows():
        folium.Marker(
            location=[row['stop_lat'], row['stop_lon']],
            popup=f"<b>En İyi Öneri:</b><br>{row['stop_name']}<br>Skor: {row['suitability_score']:.1f}",
            icon=folium.Icon(color='red', icon='star', prefix='fa'),
            tooltip=f"En İyi Öneri: {row['stop_name']}"
        ).add_to(m)
    
    # Haritayı kaydet
    m.save("GTFS/enhanced_solar_map.html")

def main():
    # Verileri yükle ve hazırla
    df = load_and_prepare_data()
    
    # Uygunluk skorunu hesapla
    df = calculate_suitability_score(df)
    
    # En iyi önerileri al
    top_recommendations = get_top_recommendations(df)
    
    # Gelişmiş haritayı oluştur
    create_enhanced_map(df, top_recommendations)
    
    # Sonuçları kaydet
    df.to_csv("GTFS/enhanced_solar_analysis.csv", index=False)
    top_recommendations.to_csv("GTFS/top_recommendations.csv", index=False)
    
    print("\nAnaliz tamamlandı!")
    print(f"Toplam durak sayısı: {len(df)}")
    print("\nEn iyi 10 öneri:")
    print(top_recommendations[['stop_name', 'suitability_score']].to_string())

if __name__ == "__main__":
    main() 