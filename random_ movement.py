import json
import math
import random
import time

# Veriyi output.json dosyasından oku
with open('output.json', 'r') as file:
    data = json.load(file)

# 100 metrelik bir vektör tanımla
vector_length = 0.001  # metre cinsinden

# Verilen bir koordinatı ve bir vektörü alarak, yeni koordinatları hesapla
def move_coordinate(x, y, length, angle_degrees):
    x_component = length * math.cos(math.radians(angle_degrees))
    y_component = length * math.sin(math.radians(angle_degrees))
    new_x = x + x_component
    new_y = y + y_component
    return new_x, new_y

while True:
    # Her hayvanın koordinatını rastgele bir yönde 100 metre hareket ettir
    for key, value in data["animnals_coords"].items():
        x = value.get("x")
        y = value.get("y")
        if x is None or y is None:
            print(f"Hata: {key} koordinatları eksik.")
        else:
            # print(f"{key}: ({x}, {y})")
            # Koordinatları rastgele bir yönde hareket ettir
            random_angle_degrees = random.uniform(0, 360)
            new_x, new_y = move_coordinate(x, y, vector_length, random_angle_degrees)
            data["animnals_coords"][key]["x"] = new_x
            data["animnals_coords"][key]["y"] = new_y

    # Sonuçları bir dosyaya yaz
    with open('output.json', 'w') as file:
        json.dump(data, file, indent=4)
        
    # 10 saniye bekle
    time.sleep(10)
