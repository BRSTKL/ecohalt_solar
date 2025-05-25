import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

# 1. Veriyi yükle
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
input_file = folder_path + "\enhanced_solar_analysis.csv"
df = pd.read_csv(input_file)

# 2. Yeni özellikler (feature engineering)
df['irradiation_per_passenger'] = df['irradiation_kWh'] / (df['passenger_density'] + 1e-6)
df['accessibility_index'] = 1 / (1 + df['metro_distance'])

# 3. Etiket oluştur (en uygun %20 durak = 1, diğerleri = 0)
threshold = df['suitability_score'].quantile(0.80)
df['label'] = (df['suitability_score'] >= threshold).astype(int)

# 4. Özellikler ve hedef değişken
target = 'label'
features = [
    'irradiation_kWh', 'passenger_density', 'metro_distance',
    'irradiation_per_passenger', 'accessibility_index'
]
X = df[features]
y = df[target]

# 5. Normalize et
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 6. SMOTE ile veri dengesizliğini düzelt
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)
print(f"Orijinal veri dağılımı: {np.bincount(y)}")
print(f"SMOTE sonrası veri dağılımı: {np.bincount(y_resampled)}")

# 7. Eğitim ve test setine ayır
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

# 8. Random Forest Modeli
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_preds = rf.predict(X_test)
rf_probs = rf.predict_proba(X_test)[:,1]

print("\nRandom Forest Sonuçları:")
print(classification_report(y_test, rf_preds))
print("ROC AUC:", roc_auc_score(y_test, rf_probs))

# 9. XGBoost Modeli
xgb = XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb.fit(X_train, y_train)
xgb_preds = xgb.predict(X_test)
xgb_probs = xgb.predict_proba(X_test)[:,1]

print("\nXGBoost Sonuçları:")
print(classification_report(y_test, xgb_preds))
print("ROC AUC:", roc_auc_score(y_test, xgb_probs))

# 10. Cross-validation ile genel başarı
rf_cv = cross_val_score(rf, X_resampled, y_resampled, cv=5, scoring='roc_auc').mean()
xgb_cv = cross_val_score(xgb, X_resampled, y_resampled, cv=5, scoring='roc_auc').mean()
print(f"\nRandom Forest CV ROC AUC: {rf_cv:.3f}")
print(f"XGBoost CV ROC AUC: {xgb_cv:.3f}")

# 11. GridSearchCV ile hiperparametre optimizasyonu
print("\n--- GridSearchCV ile Hiperparametre Optimizasyonu ---")

# Random Forest için parametreler
grid_rf = {
    'n_estimators': [100, 200],
    'max_depth': [5, 10, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}
gs_rf = GridSearchCV(RandomForestClassifier(random_state=42), grid_rf, cv=3, scoring='f1', n_jobs=-1)
gs_rf.fit(X_resampled, y_resampled)
print("Random Forest En İyi Parametreler:", gs_rf.best_params_)
print("Random Forest En İyi F1:", gs_rf.best_score_)

# XGBoost için parametreler
grid_xgb = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 10],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 1.0]
}
gs_xgb = GridSearchCV(XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42), grid_xgb, cv=3, scoring='f1', n_jobs=-1)
gs_xgb.fit(X_resampled, y_resampled)
print("XGBoost En İyi Parametreler:", gs_xgb.best_params_)
print("XGBoost En İyi F1:", gs_xgb.best_score_) 