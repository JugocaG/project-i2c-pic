#include <Wire.h>

#define SLAVE_ADDR 0x11  // Dirección del esclavo I2C (PIC)

void setup() {
    Wire.begin();             // Inicia el bus I2C
    Serial.begin(9600);       // Inicia la comunicación serial con Python
}

void loop() {
    if (Serial.available()) {
        String brightnessStr = Serial.readStringUntil('\n');
        int brightness = brightnessStr.toInt();

        if (brightness >= 0 && brightness <= 255) {
            Wire.beginTransmission(SLAVE_ADDR);
            Wire.write(brightness);
            Wire.endTransmission();

            Serial.print("Brillo enviado al PIC: ");
            Serial.println(brightness);
        } else {
            Serial.println("Valor fuera de rango o no válido.");
        }
    }
}

