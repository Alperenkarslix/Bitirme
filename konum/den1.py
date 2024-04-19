import json

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

    def which_side(self, point):
        # Verilen noktanın dikdörtgenin hangi tarafında olduğunu belirle
        x, y = point
        if x < self.top_left[0]:
            return "sol"
        elif x > self.top_right[0]:
            return "sağ"
        elif y < self.top_left[1]:
            return "üst"
        elif y > self.bottom_left[1]:
            return "alt"
        else:
            return "içinde"

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
top_left = camera_coords[0]
top_right = camera_coords[1]
bottom_left = camera_coords[3]
bottom_right = camera_coords[2]

# Dikdörtgen oluşturma
rectangle = Rectangle(top_left, top_right, bottom_left, bottom_right)

# Hayvan konumları
animal_data = data['animnals_coords']
animals = [Animal((animal['x'], animal['y']), animal['name'], animal['temperature']) for animal in animal_data.values()]

# Hayvanların konumlarını kontrol etme
for animal in animals:
    if rectangle.is_inside(animal.position):
        print(f"{animal.name}, dikdörtgenin içinde.")
    else:
        side = rectangle.which_side(animal.position)
        print(f"{animal.name}, dikdörtgenin {side} tarafında.")
