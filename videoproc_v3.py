import cv2
import json
from shapely.geometry import Point, Polygon
from ultralytics import YOLO

# Video dosyasını aç
video_path = "videos/testvideo.mp4"  # Video dosyasının yolunu belirtin
cap = cv2.VideoCapture(video_path)


# Video boyutlarını al
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Köşe noktalarını belirle
corner_points = {
    "Sag Alt": (width - 260, height - 10),
    "Sag Ust": (width - 260, 20),
    "Sol Ust": (0, 20),
    "Sol Alt": (0, height - 7)
}
edge_names = ["Sag Taraf","Ust Taraf","Sol Taraf","Alt Taraf"]

def calculate_pixel_coordinates(lat, lon, corner_coords, image_dimensions):
    # Unpack corner coordinates and image dimensions
    (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4) = corner_coords
    image_width, image_height = image_dimensions
    
    # Calculate center latitude and longitude by averaging the corners
    center_lat = (lat1 + lat2 + lat3 + lat4) / 4
    center_lon = (lon1 + lon2 + lon3 + lon4) / 4
    
    # Calculate pixel scale assuming uniform latitude and longitude scaling
    lat_scale = image_height / (max(lat1, lat2, lat3, lat4) - min(lat1, lat2, lat3, lat4))
    lon_scale = image_width / (max(lon1, lon2, lon3, lon4) - min(lon1, lon2, lon3, lon4))
    
    # Convert latitude and longitude to pixel coordinates
    x = image_width / 2 + (lon - center_lon) * lon_scale
    y = image_height / 2 - (lat - center_lat) * lat_scale
    
    return int(x), int(y)

# Videoyu açık tut
while(cap.isOpened()):
    # Video çerçevesini oku
    ret, frame = cap.read()
    if not ret:
        break

    # JSON dosyasını aç
    json_file = "output.json"
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    # Köşelere metinleri yazdır
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    text_color = (255, 255, 255) 
    for corner, coord in corner_points.items():
        index = list(corner_points.keys()).index(corner)
        x, y = data['camera_coords'][index]
        text = f"{x:.6f}, {y:.6f}"
        cv2.putText(frame, text, coord, font, font_scale, text_color, font_thickness, cv2.LINE_AA)

    # Dikdörtgenin köşe noktalarını belirle
    rect_coords = [data["camera_coords"][0], data["camera_coords"][1], data["camera_coords"][2], data["camera_coords"][3]]
    rect_polygon = Polygon(rect_coords)

    # Başlangıç yüksekliği
    y_offset = 50

    # Her hayvan için kontrol et
    for animal_key, animal_data in data['animal_coords'].items():
        animal_x = animal_data['x']
        animal_y = animal_data['y']
        animal_point = Point(animal_x, animal_y)
        
        # Hayvanın konumunu dikdörtgenin içinde mi dışında mı kontrol et
        if rect_polygon.contains(animal_point):
            cv2.putText(frame, f"{animal_data['name']} icinde", (0, y_offset), font, 0.5, text_color, 1, cv2.LINE_AA)
            animal_pixel_x, animal_pixel_y = calculate_pixel_coordinates(animal_x, animal_y, rect_coords, (width, height))
            # Küçük bir yeşil kare oluşturarak hayvanı göster
            cv2.rectangle(frame, (animal_pixel_x - 10, animal_pixel_y - 10), (animal_pixel_x + 10, animal_pixel_y + 10), (255, 0, 0), 1)
            # Hayvanın ismini ve uzaklığını altına yazdır
            text = f"{animal_data['name']}: Sicaklik{animal_data['temperature']:.2f}"
            text_width, text_height = cv2.getTextSize(text, font, 0.5, 1)[0]
            text_x = animal_pixel_x - text_width // 2
            text_y = animal_pixel_y + 20
            cv2.putText(frame, text, (text_x, text_y), font, 0.5, text_color, 1, cv2.LINE_AA)
        else:
            # Hayvanın dikdörtgenin hangi kenarına daha yakın olduğunu bul
            nearest_side_index = None
            min_distance = float('inf')
            for i, (start_x, start_y) in enumerate(rect_coords):
                end_x, end_y = rect_coords[(i + 1) % 4]
                side_center_x = (start_x + end_x) / 2
                side_center_y = (start_y + end_y) / 2
                distance = ((animal_x - side_center_x) ** 2 + (animal_y - side_center_y) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    nearest_side_index = i

            # En yakın kenarın ismini al
            nearest_side_name = edge_names[nearest_side_index]
            
            # Hayvanın ekran dışında olduğu ve en yakın kenarı yazdır
            cv2.putText(frame, f"{animal_data['name']} disinda ({nearest_side_name})", (0, y_offset), font, 0.5, text_color, 1, cv2.LINE_AA)
            
            # Get dimensions of the frame
            height, width = frame.shape[:2]
            # Calculate target pixel coordinates from geographic coordinates
            target_x, target_y = calculate_pixel_coordinates(animal_x, animal_y, rect_coords, (width, height))

            # Draw a red arrow from center to the target point
            center_x, center_y = width // 2, height // 2
            
            # Hedef noktanın ekran sınırlarını kontrol et
            if target_x < 0:
                target_x = 0
            elif target_x > width:
                target_x = width
            if target_y < 0:
                target_y = 0
            elif target_y > height:
                target_y = height

            # Okun başlangıç noktasını hesapla
            arrow_length = ((target_x - center_x) ** 2 + (target_y - center_y) ** 2) ** 0.5
            if arrow_length > 40:
                ratio = 40 / arrow_length
                start_x = int(target_x + (center_x - target_x) * ratio)
                start_y = int(target_y + (center_y - target_y) * ratio)

            # Ok çizimi
            cv2.arrowedLine(frame, (start_x, start_y), (target_x, target_y), (0, 255, 0), 2)

            # Hayvanın ismini ve uzaklığını yazdır
            text = f"{animal_data['name']}: {animal_data['distance_metre']:.2f} metre Sicaklik{animal_data['temperature']:.2f}"
            text_width, text_height = cv2.getTextSize(text, font, 0.5, 1)[0]
            text_x = start_x if start_x + text_width + 10 < width else width - text_width - 10
            text_y = start_y + 20
            cv2.putText(frame, text, (text_x, text_y), font, 0.5, text_color, 1, cv2.LINE_AA)
                
        # Yüksekliği artır
        y_offset += 30

    # İşlenen çerçeveyi göster
    cv2.imshow('Video', frame)
    
    # q tuşuna basılınca videoyu kapat
    key = cv2.waitKey(1)
    if key == ord('y'):
        # Load the YOLO model
        model = YOLO('yolomodels/animals-4/detect/train/weights/best.pt')

        # Print the class names
        print(model.names)

        # Run the YOLO model to get tracking results
        results = model.track(frame, classes=0, conf=0.8, imgsz=320)

        # Extract the number of boxes detected
        num_boxes = len(results[0].boxes)

        # Add text to the frame showing the total number of detections
        #cv2.putText(frame, f"Total: {num_boxes}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # Plot the results on the frame
        plotted_frame = results[0].plot()

        # Display the frame with detections
        #cv2.imshow("Live Camera", plotted_frame)

        # Break the loop if 'y' is pressed
        if cv2.waitKey(1) == ord('y'):
            break
    elif key == ord('q'):
        break

# Açılan pencereleri kapat
cap.release()
cv2.destroyAllWindows()