#include <16F877A.h>
#fuses XT, NOWDT, NOPROTECT, NOLVP
#use delay(clock=4000000)
#use i2c(SLAVE, SDA=PIN_C4, SCL=PIN_C3, address=0x22, FORCE_HW)

#define LED_VERDE_IZQ PIN_A0
#define LED_AMARILLO_IZQ PIN_A1
#define LED_ROJO_IZQ PIN_A2
#define LED_VERDE_DER PIN_B7
#define LED_AMARILLO_DER PIN_B6
#define LED_ROJO_DER PIN_B5

void apagar_todos_leds() {
    output_low(LED_VERDE_IZQ);
    output_low(LED_AMARILLO_IZQ);
    output_low(LED_ROJO_IZQ);
    output_low(LED_VERDE_DER);
    output_low(LED_AMARILLO_DER);
    output_low(LED_ROJO_DER);
}

void encenderLedsPorComando(char comando) {
    apagar_todos_leds();  // Apagar todos los LEDs antes de encender los nuevos

    switch (comando) {
        case 'A':  // Verde Izquierda, Rojo Derecha
            output_high(LED_VERDE_IZQ);
            output_high(LED_ROJO_DER);
            break;
        case 'B':  // Amarillo Izquierda, Rojo Derecha
            output_high(LED_AMARILLO_IZQ);
            output_high(LED_ROJO_DER);
            output_high(LED_AMARILLO_DER);
            break;
        case 'C':  // Rojo Izquierda, Verde Derecha
            output_high(LED_ROJO_IZQ);
            output_high(LED_VERDE_DER);
            break;
        case 'D':  // Rojo Izquierda, Amarillo Derecha
            output_high(LED_ROJO_IZQ);
            output_high(LED_AMARILLO_IZQ);
            output_high(LED_AMARILLO_DER);
            break;
        default:  // Apagar todos si llega un comando inv�lido
            apagar_todos_leds();
            break;
    }
}

#INT_SSP
void i2c_isr() {
    char comando = i2c_read();  // Leer un solo car�cter enviado por el Arduino
    encenderLedsPorComando(comando);  // Encender los LEDs seg�n el comando recibido
}

void main() {
    enable_interrupts(INT_SSP);   // Habilitar interrupciones I2C
    enable_interrupts(GLOBAL);   // Habilitar interrupciones globales

    while (TRUE) {
        // Espera a que lleguen comandos
    }
}

