#include <16F877A.h>
#fuses XT, NOWDT, NOPROTECT, NOLVP
#use delay(clock=4000000)
#use i2c(SLAVE, SDA=PIN_C4, SCL=PIN_C3, address=0x22, FORCE_HW)  // Dirección esclavo I2C

#define PWM_PIN PIN_C2  // Pin CCP1 (PWM1) para controlar el LED

void main() {
    setup_ccp1(CCP_PWM);       // Configura CCP1 como PWM
    setup_timer_2(T2_DIV_BY_16, 255, 1);  // Configura Timer2 para PWM a ~490 Hz

    set_pwm1_duty(0);  // Apaga el LED al inicio

    int brightness = 0;  // Valor de brillo recibido

    while (TRUE) {
        if (i2c_poll()) {           // Verifica si hay datos I2C disponibles
            brightness = i2c_read(); // Lee el valor de brillo enviado por el Arduino
            set_pwm1_duty((long)brightness * 4);  // Ajusta el ciclo de trabajo PWM (0 a 1023)
        }
    }
}


