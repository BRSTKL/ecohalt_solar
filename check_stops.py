import pandas as pd
import os

# Dosya yolu
folder_path = r"D:\Masaüstü\EcoHalt Solar\GTFS"
stops_file = os.path.join(folder_path, "stops.txt")

# Durakları oku
df = pd.read_csv(stops_file)

# Otobüs ve tramvay duraklarını filtrele
bus_tram_stops = df[df['stop_name'].str.contains('Bus|Tram|bus|tram', na=False)]

print(f"Toplam durak sayısı: {len(df)}")
print(f"Otobüs ve tramvay durağı sayısı: {len(bus_tram_stops)}")

# İlk 5 durağı göster
print("\nİlk 5 otobüs/tramvay durağı:")
print(bus_tram_stops[['stop_name', 'stop_lat', 'stop_lon']].head()) 