import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
import os
import joblib
import numpy as np

def load_and_prepare_data():
    """Verileri yükle ve hazırla"""
    # Dosya yolu
    folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
    input_file = os.path.join(folder_path, "enhanced_solar_analysis.csv")
    
    # Veriyi oku
    df = pd.read_csv(input_file)
    
    # Etiket oluştur (en uygun %20 durak = 1, diğerleri = 0)
    threshold = df['suitability_score'].quantile(0.80)
    df['label'] = (df['suitability_score'] >= threshold).astype(int)
    
    return df

def train_model(df):
    """Modeli eğit ve değerlendir"""
    # Giriş değişkenleri (özellikler)
    features = ['irradiation_kWh', 'passenger_density', 'metro_distance']
    X = df[features]
    y = df['label']
    
    # Normalize et
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Eğitim ve test setine ayır
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # Random Forest Modeli
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    # Modeli eğit
    model.fit(X_train, y_train)
    
    # Test seti üzerinde tahmin yap
    preds = model.predict(X_test)
    
    # Sonuçları yazdır
    print("\n🔍 Classification Report:")
    print(classification_report(y_test, preds))
    
    print("\n📉 Confusion Matrix:")
    print(confusion_matrix(y_test, preds))
    
    # Özellik önemliliklerini yazdır
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📊 Özellik Önemlilikleri:")
    print(feature_importance)
    
    return model, scaler, features

def save_model(model, scaler, features):
    """Modeli ve scaler'ı kaydet"""
    folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
    
    # Modeli kaydet
    model_path = os.path.join(folder_path, "solar_stop_model.joblib")
    joblib.dump(model, model_path)
    
    # Scaler'ı kaydet
    scaler_path = os.path.join(folder_path, "solar_stop_scaler.joblib")
    joblib.dump(scaler, scaler_path)
    
    # Özellik listesini kaydet
    features_path = os.path.join(folder_path, "model_features.txt")
    with open(features_path, 'w') as f:
        f.write('\n'.join(features))
    
    print(f"\n✅ Model kaydedildi: {model_path}")
    print(f"✅ Scaler kaydedildi: {scaler_path}")
    print(f"✅ Özellik listesi kaydedildi: {features_path}")

def predict_new_stops(model, scaler, features):
    """Yeni duraklar için tahmin yap"""
    # Örnek yeni duraklar
    new_stops = pd.DataFrame({
        'irradiation_kWh': [1200, 1100, 1300],
        'passenger_density': [80, 60, 90],
        'metro_distance': [500, 1000, 300]
    })
    
    # Verileri normalize et
    X_new = scaler.transform(new_stops[features])
    
    # Tahmin yap
    predictions = model.predict(X_new)
    probabilities = model.predict_proba(X_new)
    
    # Sonuçları yazdır
    print("\n🔮 Yeni Duraklar için Tahminler:")
    for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
        print(f"\nDurak {i+1}:")
        print(f"Güneşlenme: {new_stops['irradiation_kWh'][i]} kWh/yıl")
        print(f"Yolcu Yoğunluğu: {new_stops['passenger_density'][i]}")
        print(f"Metro Uzaklığı: {new_stops['metro_distance'][i]} m")
        print(f"Tahmin: {'Uygun' if pred == 1 else 'Uygun Değil'}")
        print(f"Uygunluk Olasılığı: {prob[1]:.2%}")

def main():
    # Verileri yükle
    df = load_and_prepare_data()
    
    # Modeli eğit
    model, scaler, features = train_model(df)
    
    # Modeli kaydet
    save_model(model, scaler, features)
    
    # Yeni duraklar için tahmin yap
    predict_new_stops(model, scaler, features)

if __name__ == "__main__":
    main() 