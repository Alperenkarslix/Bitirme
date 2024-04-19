import math
import json

# Kuş uçuşu mesafe
def hesapla_kus(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

# Metre olarak mesafe
def hesapla_metre(coord1, coord2):
    # Dereceleri radyanlara dönüştür
    lat1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])

    # İki nokta arasındaki enlem ve boylam farkını hesapla
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine formülünü kullanarak uzaklığı hesapla
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371000  # Earth's radius in meters
    distancem = R * c

    return distancem

# Veriyi output.json dosyasından oku
with open('output.json', 'r') as file:
    data = json.load(file)


    # Her hayvanın koordinatını rastgele bir yönde 100 metre hareket ettir
for key, value in data["animal_coords"].items():
    x = value.get("x")
    y = value.get("y")
    iha_x = data["center_x"]
    iha_y = data["center_y"]
    if x is None or y is None:
        print(f"Hata: {key} koordinatları eksik.")
    else:
        # print(f"{key}: ({x}, {y})")
        # Koordinatları rastgele bir yönde hareket ettir
        data["animal_coords"][key]["distance_metre"] = hesapla_metre((iha_x, iha_y), (x,y))
        # data["animal_coords"][key]["kus_ucusu"] = new_y

# Sonuçları bir dosyaya yaz
with open('output.json', 'w') as file:
    json.dump(data, file, indent=4)
        
