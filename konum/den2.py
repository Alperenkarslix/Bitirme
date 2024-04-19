import cv2
import json
import numpy as np

class Rectangle:
    def __init__(self, top_left, top_right, bottom_left, bottom_right):
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right

    def is_inside(self, point):
        # Verilen noktanın dikdörtgenin içinde olup olmadığını kontrol et
        x, y = point
        return self.top_left[0] < x < self.top_right[0] and self.top_left[1] < y < self.bottom_left[1]

    def nearest_edge(self, point):
        # Verilen noktaya en yakın kenarı bul
        x, y = point
        distances = [
            np.linalg.norm(np.array(self.top_left) - np.array((x, y))),
            np.linalg.norm(np.array(self.top_right) - np.array((x, y))),
            np.linalg.norm(np.array(self.bottom_left) - np.array((x, y))),
            np.linalg.norm(np.array(self.bottom_right) - np.array((x, y)))
        ]
        min_index = np.argmin(distances)
        if min_index == 0:
            return self.top_left, self.top_right
        elif min_index == 1:
            return self.top_right, self.bottom_right
        elif min_index == 2:
            return self.bottom_left, self.top_left
        elif min_index == 3:
            return self.bottom_right, self.bottom_left

class Animal:
    def __init__(self, position, name, temperature):
        self.position = position
        self.name = name
        self.temperature = temperature

# JSON dosyasından verileri oku
with open('output.json', 'r') as f:
    data = json.load(f)

# Kamera koordinatlarını al
camera_coords = data['camera_coords']

# Dikdörtgenin köşe koordinatları olarak kamera koordinatlarını kullan
top_left = tuple(map(float, camera_coords[0]))
top_right = tuple(map(float, camera_coords[1]))
bottom_left = tuple(map(float, camera_coords[3]))
bottom_right = tuple(map(float, camera_coords[2]))

# Dikdörtgen oluşturma
rectangle = Rectangle(top_left, top_right, bottom_left, bottom_right)

# Hayvan konumları
animal_data = data['animnals_coords']
animals_inside = []
animals_outside = []
for animal_info in animal_data.values():
    position = (float(animal_info['x']), float(animal_info['y']))
    animal = Animal(position, animal_info['name'], animal_info['temperature'])
    if rectangle.is_inside(position):
        animals_inside.append(animal)
    else:
        animals_outside.append(animal)

# Çerçeve oluşturma
frame_width, frame_height = 800, 600
frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# Dörtgen içinde olan hayvanları mavi noktalarla gösterme
for animal in animals_inside:
    x, y = animal.position
    cv2.circle(frame, (int(x), int(y)), 2, (255, 0, 0), -1)

# Dışında olan hayvanları en yakın kenara sarı oklarla gösterme
for animal in animals_outside:
    x, y = animal.position
    nearest_edge_start, nearest_edge_end = rectangle.nearest_edge((x, y))
    cv2.arrowedLine(frame, (int(x), int(y)), (int(nearest_edge_start[0]), int(nearest_edge_start[1])), (0, 255, 255), 1)

# Çerçeveyi gösterme
cv2.imshow('Frame', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
