import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import joblib
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="EcoHalt Solar - Durak Analizi",
    page_icon="☀️",
    layout="wide"
)

# Başlık
st.title("☀️ EcoHalt Solar - Durak Analizi")
st.markdown("Berlin'deki otobüs ve tramvay duraklarının güneş enerjisi potansiyeli analizi")

# Model ve scaler'ı yükle
@st.cache_resource
def load_model():
    folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
    model = joblib.load(os.path.join(folder_path, "solar_stop_model.joblib"))
    scaler = joblib.load(os.path.join(folder_path, "solar_stop_scaler.joblib"))
    with open(os.path.join(folder_path, "model_features.txt"), 'r') as f:
        features = f.read().splitlines()
    return model, scaler, features

# Verileri yükle
@st.cache_data
def load_data():
    df = pd.read_csv("GTFS/enhanced_solar_analysis.csv")
    return df

# Ana veri setini yükle
df = load_data()
model, scaler, features = load_model()

# Sidebar filtreleri
st.sidebar.header("Filtreler")

# Durak adı filtresi
stop_name = st.sidebar.text_input("Durak Adı Ara", "")

# Güneşlenme aralığı filtresi
min_irradiation = df['irradiation_kWh'].min()
max_irradiation = df['irradiation_kWh'].max()
irradiation_range = st.sidebar.slider(
    "Güneşlenme Aralığı (kWh/yıl)",
    min_value=float(min_irradiation),
    max_value=float(max_irradiation),
    value=(float(min_irradiation), float(max_irradiation))
)

# Uygunluk skoru filtresi
min_score = df['suitability_score'].min()
max_score = df['suitability_score'].max()
score_range = st.sidebar.slider(
    "Uygunluk Skoru Aralığı",
    min_value=float(min_score),
    max_value=float(max_score),
    value=(float(min_score), float(max_score))
)

# Metro uzaklığı filtresi
max_metro_distance = st.sidebar.number_input(
    "Maksimum Metro Uzaklığı (m)",
    min_value=0,
    max_value=int(df['metro_distance'].max()),
    value=int(df['metro_distance'].max())
)

# Yeni durak tahmini
st.sidebar.header("Yeni Durak Tahmini")
st.sidebar.markdown("Yeni bir durak için uygunluk tahmini yapın:")

new_irradiation = st.sidebar.number_input(
    "Güneşlenme (kWh/yıl)",
    min_value=float(min_irradiation),
    max_value=float(max_irradiation),
    value=float(min_irradiation)
)

new_passenger_density = st.sidebar.number_input(
    "Yolcu Yoğunluğu",
    min_value=0.0,
    max_value=100.0,
    value=50.0
)

new_metro_distance = st.sidebar.number_input(
    "Metro Uzaklığı (m)",
    min_value=0,
    max_value=2000,
    value=1000
)

if st.sidebar.button("Tahmin Yap"):
    # Yeni durak verilerini hazırla
    new_stop = pd.DataFrame({
        'irradiation_kWh': [new_irradiation],
        'passenger_density': [new_passenger_density],
        'metro_distance': [new_metro_distance]
    })
    
    # Verileri normalize et
    X_new = scaler.transform(new_stop[features])
    
    # Tahmin yap
    probability = model.predict_proba(X_new)[0][1]
    threshold = 0.3  # Olasılık eşiği
    prediction = int(probability > threshold)
    
    # Sonuçları göster
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Tahmin Sonucu")
    st.sidebar.markdown(f"**Uygunluk:** {'✅ Uygun' if prediction == 1 else '❌ Uygun Değil'}")
    st.sidebar.markdown(f"**Uygunluk Olasılığı:** {probability:.2%}")

# Filtreleri uygula
mask = (
    df['stop_name'].str.contains(stop_name, case=False, na=False, regex=False) &
    (df['irradiation_kWh'] >= irradiation_range[0]) &
    (df['irradiation_kWh'] <= irradiation_range[1]) &
    (df['suitability_score'] >= score_range[0]) &
    (df['suitability_score'] <= score_range[1]) &
    (df['metro_distance'] <= max_metro_distance)
)
filtered_df = df[mask]

# İki sütunlu layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Durak Haritası")
    # Sadece geçerli ve sayısal koordinatlara sahip satırları al
    df_valid = filtered_df.dropna(subset=['stop_lat', 'stop_lon']).copy()
    df_valid = df_valid[
        df_valid['stop_lat'].apply(lambda x: pd.notnull(x) and isinstance(x, (int, float))) &
        df_valid['stop_lon'].apply(lambda x: pd.notnull(x) and isinstance(x, (int, float)))
    ]

    if not df_valid.empty:
        center_lat = df_valid['stop_lat'].mean()
        center_lon = df_valid['stop_lon'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        for idx, row in df_valid.iterrows():
            # Satırda NaN veya tip hatası varsa marker ekleme
            if pd.isnull(row['stop_lat']) or pd.isnull(row['stop_lon']):
                continue
            if not isinstance(row['stop_lat'], (int, float)) or not isinstance(row['stop_lon'], (int, float)):
                continue

            popup_content = f"""
            <div style='font-family: Arial; width: 200px;'>
                <h4 style='margin-bottom: 5px;'>{row['stop_name']}</h4>
                <p style='margin: 2px 0;'>Güneşlenme: {row['irradiation_kWh']:.1f} kWh/yıl</p>
                <p style='margin: 2px 0;'>Metro Uzaklığı: {row['metro_distance']:.0f} m</p>
                <p style='margin: 2px 0;'>Yolcu Yoğunluğu: {row['passenger_density']:.1f}</p>
                <p style='margin: 2px 0;'>Uygunluk Skoru: {row['suitability_score']:.1f}</p>
            </div>
            """
            folium.CircleMarker(
                location=[row['stop_lat'], row['stop_lon']],
                radius=5,
                popup=folium.Popup(popup_content, max_width=300),
                color='red' if row['suitability_score'] > 80 else 'orange' if row['suitability_score'] > 50 else 'green',
                fill=True,
                fill_opacity=0.7,
                tooltip=row['stop_name']
            ).add_to(m)

        folium_static(m, width=800, height=600)
    else:
        st.warning("⚠️ Uygulanan filtrelerle eşleşen geçerli konumda durak bulunamadı. Lütfen filtreleri genişletin.")

with col2:
    # İstatistikler
    st.subheader("İstatistikler")
    st.metric("Filtrelenmiş Durak Sayısı", len(filtered_df))
    st.metric("Ortalama Güneşlenme", f"{filtered_df['irradiation_kWh'].mean():.1f} kWh/yıl")
    st.metric("Ortalama Uygunluk Skoru", f"{filtered_df['suitability_score'].mean():.1f}")
    
    # En iyi 5 durak
    st.subheader("En İyi 5 Durak")
    top_5 = filtered_df.nlargest(5, 'suitability_score')
    for idx, row in top_5.iterrows():
        st.markdown(f"""
        **{row['stop_name']}**  
        Güneşlenme: {row['irradiation_kWh']:.1f} kWh/yıl  
        Skor: {row['suitability_score']:.1f}
        ---
        """)
    
    # Güneşlenme dağılımı grafiği
    st.subheader("Güneşlenme Dağılımı")
    fig = px.histogram(
        filtered_df,
        x='irradiation_kWh',
        nbins=20,
        title='Güneşlenme Dağılımı'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Özellik önemlilikleri grafiği
    st.subheader("Özellik Önemlilikleri")
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=True)
    
    fig = px.bar(
        feature_importance,
        x='importance',
        y='feature',
        orientation='h',
        title='Özellik Önemlilikleri'
    )
    st.plotly_chart(fig, use_container_width=True)

# Alt bilgi
st.markdown("---")
st.markdown("© 2024 EcoHalt Solar - Tüm hakları saklıdır.") 