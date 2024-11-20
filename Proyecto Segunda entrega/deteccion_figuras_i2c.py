import cv2
import time
import serial

# Configurar la comunicación serial con Arduino
arduino = serial.Serial('COM4', 9600)  # Cambia 'COM4' según tu puerto
time.sleep(2)  # Espera para estabilizar la conexión

def enviar_comando(comando):
    """Envía un comando al Arduino."""
    arduino.write(comando.encode())
    print(f"Comando enviado: {comando}")

def calcular_tiempos(count_left, count_right, ciclo_total=60):
    """Calcula el tiempo verde para cada carril basado en el conteo de vehículos."""
    total_vehiculos = count_left + count_right
    if total_vehiculos == 0:
        return ciclo_total // 2, ciclo_total // 2  # 30s para cada carril si no hay vehículos

    tiempo_izquierda = (count_left / total_vehiculos) * ciclo_total
    tiempo_derecha = (count_right / total_vehiculos) * ciclo_total

    return int(tiempo_izquierda), int(tiempo_derecha)

# Especifica la ubicación de los archivos del modelo MobileNet SSD.
prototxt = "Proyecto Segunda entrega/model/MobileNetSSD_deploy.prototxt.txt"
model = "Proyecto Segunda entrega/model/MobileNetSSD_deploy.caffemodel"

# Define un diccionario que asocia números de clases a etiquetas relevantes.
filtered_classes = {
    2: "bicycle",
    6: "bus",
    7: "carro",
    14: "motorbike",
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
    count_left_zone_vehicles = 0
    count_right_zone_vehicles = 0

    for detection in detections[0][0]:
        confidence = detection[2]
        if confidence > 0.45:
            class_id = int(detection[1])
            label = filtered_classes.get(class_id, None)
            
            if label:
                box = detection[3:7] * [width, height, width, height]
                x_start, y_start, x_end, y_end = box.astype(int)
                
                # Dibuja el rectángulo y muestra la etiqueta.
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x_start, y_start - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Determina el centro del objeto.
                object_center_x = (x_start + x_end) // 2

                # Contar vehículos en cada zona.
                if label in ["bicycle", "bus", "carro", "motorbike", "tren"]:
                    if object_center_x < mid_x:
                        count_left_zone_vehicles += 1
                    else:
                        count_right_zone_vehicles += 1

    # Total de vehículos
    total_vehicles = count_left_zone_vehicles + count_right_zone_vehicles

    # Calcula el tiempo verde para cada carril
    tiempo_verde_izq, tiempo_verde_der = calcular_tiempos(count_left_zone_vehicles, count_right_zone_vehicles)
    
    # Imprimir resultados
    print(f"Total Vehiculos: {total_vehicles}, Izquierda: {count_left_zone_vehicles}, Derecha: {count_right_zone_vehicles}")
    print(f"Tiempo Verde Izquierda: {tiempo_verde_izq}s, Tiempo Verde Derecha: {tiempo_verde_der}s")

    # Estado 1: Izquierda Verde, Derecha Rojo
    enviar_comando('A')
    time.sleep(tiempo_verde_izq)

    # Estado 2: Izquierda Amarillo, Derecha Rojo
    enviar_comando('B')
    time.sleep(4)

    # Estado 3: Izquierda Rojo, Derecha Verde
    enviar_comando('C')
    time.sleep(tiempo_verde_der)

    # Estado 4: Izquierda Rojo, Derecha Amarillo
    enviar_comando('D')
    time.sleep(4)

    # Muestra los conteos en el frame.
    cv2.putText(frame, f"Vehiculos Izquierda: {count_left_zone_vehicles}", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, f"Vehiculos Derecha: {count_right_zone_vehicles}", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    cv2.putText(frame, f"Total Vehiculos: {total_vehicles}", (10, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Muestra el fotograma.
    cv2.imshow("Detección de Vehículos", frame)
    
    # Permitir cerrar la ventana con la tecla ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Libera recursos y cierra ventanas.
cap.release()
cv2.destroyAllWindows()
