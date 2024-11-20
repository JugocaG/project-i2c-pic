#include <Wire.h>

void setup() {
    Wire.begin();  // Iniciar I2C
    Serial.begin(9600);  // Comunicación con Python para depuración
}

void loop() {
    if (Serial.available()) {
        char comando = Serial.read();  // Leer un carácter desde Python

        // Enviar comando al PIC
        Wire.beginTransmission(0x11);  // Dirección I2C del PIC
        Wire.write(comando);           // Enviar comando como un solo byte
        Wire.endTransmission();

        // Mostrar en el monitor serial para depuración
        Serial.print("Comando enviado al PIC: ");
        Serial.println(comando);
    }
}
