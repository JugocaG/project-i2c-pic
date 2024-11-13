import serial
import time

# Configuración del puerto serial para el Arduino
arduino_port = 'COM61'  # Ajusta según el puerto de tu Arduino
baud_rate = 9600
arduino = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Espera 2 segundos para estabilizar la conexión

def control_led(state):
    if state in ['1', '0']:
        arduino.write(state.encode())  # Envía '1' o '0' al Arduino
        print(f"Comando enviado: {state}")
    else:
        print("Entrada inválida. Use '1' para encender o '0' para apagar el LED.")

try:
    while True:
        user_input = input("Ingrese '1' para encender el LED o '0' para apagarlo (o 'q' para salir): ")
        if user_input.lower() == 'q':
            print("Saliendo...")
            break
        control_led(user_input)
finally:
    arduino.close()  # Cierra la conexión serial cuando termina el programa
