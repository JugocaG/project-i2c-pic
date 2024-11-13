import cv2
import mediapipe as mp
import serial
import time
import numpy as np

class HandTracker:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, modelComplexity=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def handsFinder(self, image, draw=True):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)
        return image

    def positionFinder(self, image):
        lmlist = []
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[0]
            for id in [4, 8]:  # Pulgar e índice
                lm = Hand.landmark[id]
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
        return lmlist

# Configuración serial con Arduino
arduino = serial.Serial('COM6', 9600)
time.sleep(2)

def send_brightness_to_arduino(brightness):
    arduino.write(f"{brightness}\n".encode())
    print(f"Brillo enviado al Arduino: {brightness}")

def main():
    cap = cv2.VideoCapture(1)
    tracker = HandTracker()

    last_calc_time = time.time()  # Tiempo de la última actualización de distancia y brillo
    calc_interval = 0.2  # Intervalo en segundos entre cálculos (200 ms)

    while True:
        success, image = cap.read()
        image = tracker.handsFinder(image)
        lmList = tracker.positionFinder(image)

        if len(lmList) == 2:  # Pulgar e índice detectados
            thumb_x, thumb_y = lmList[0][1], lmList[0][2]
            index_x, index_y = lmList[1][1], lmList[1][2]

            current_time = time.time()
            if current_time - last_calc_time >= calc_interval:
                distance = np.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
                brightness = np.clip(np.interp(distance, [30, 200], [0, 255]), 0, 255)
                send_brightness_to_arduino(int(brightness))

                # Actualizar el tiempo de la última medición
                last_calc_time = current_time

            # Mostrar siempre la distancia visualmente, aunque no se envíe al Arduino
            distance = np.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
            cv2.putText(image, f'Distancia: {int(distance)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.line(image, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3)

        cv2.imshow("Video", image)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    arduino.close()

if __name__ == "__main__":
    main()
