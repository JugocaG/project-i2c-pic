import cv2
import time

# Especifica la ubicación de los archivos del modelo MobileNet SSD.
prototxt = "Proyecto Segunda entrega/model/MobileNetSSD_deploy.prototxt.txt"
model = "Proyecto Segunda entrega/model/MobileNetSSD_deploy.caffemodel"

# Define un diccionario que asocia números de clases a etiquetas relevantes.
filtered_classes = {
    2: "bicycle",
    6: "bus",
    7: "carro",
    14: "motorbike",
    15: "persona",
    19: "tren"
}

# Carga el modelo MobileNet SSD desde los archivos prototxt y caffemodel.
try:
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
except Exception as e:
    print("Error al cargar el modelo:", e)
    exit()

# Abre un archivo de video o usa la cámara web en tiempo real.
cap = cv2.VideoCapture(0)  # Cambia el índice si no detecta la cámara correcta.

# Calcula FPS para monitorear rendimiento.
fps_start_time = time.time()
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer el video/cámara.")
        break

    height, width, _ = frame.shape
    mid_x = width // 2  # División del cuadro en dos mitades (izquierda y derecha)

    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), (127.5, 127.5, 127.5))
    net.setInput(blob)
    detections = net.forward()

    # Contadores
    count_left_zone = 0
    count_right_zone = 0

    for detection in detections[0][0]:
        confidence = detection[2]
        if confidence > 0.45:
            class_id = int(detection[1])
            label = filtered_classes.get(class_id, None)
            
            if label == "persona":  # Solo cuenta personas en las zonas
                box = detection[3:7] * [width, height, width, height]
                x_start, y_start, x_end, y_end = box.astype(int)
                
                # Dibuja el rectángulo y muestra la etiqueta.
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x_start, y_start - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Determina en qué zona está la persona
                person_center_x = (x_start + x_end) // 2
                if person_center_x < mid_x:
                    count_left_zone += 1
                else:
                    count_right_zone += 1

    # Muestra los conteos en el frame.
    cv2.putText(frame, f"Personas Izquierda: {count_left_zone}", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Personas Derecha: {count_right_zone}", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Muestra FPS en la esquina superior izquierda.
    frame_count += 1
    elapsed_time = time.time() - fps_start_time
    fps = frame_count / elapsed_time
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Muestra el fotograma.
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Libera recursos y cierra ventanas.
cap.release()
cv2.destroyAllWindows()