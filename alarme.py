import RPi.GPIO as GPIO
import time
import lcd

# Definindo como configurar a GPIO (físico)
GPIO.setmode(GPIO.BOARD)
# GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Definindo os pinos dos componentes
ledAlarme = 40
# ledAlarme = 13
ledCompartimento = [38, 36]
# ledCompartimento = [12, 5]
buzzer = 32
# buzzer = 23
botao = 26
# botao = 26


# Definindo os pinos dos LED's e do buzzer como saídas
GPIO.setup(ledAlarme, GPIO.OUT)
# for compartimento in range(0, 2):
#     GPIO.setup(ledCompartimento[compartimento], GPIO.OUT)

for compartimento in ledCompartimento:
    GPIO.setup(compartimento, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)


# Definindo o pino do botão como entrada
GPIO.setup(botao, GPIO.IN)


# Configurações iniciais do I2C, do buzzer e do LED de alarme
# lcdi2c = I2C_LCD_driver.lcd()
buzzState = False
ledAlarmeState = False

def semAlarme(compartimento):
    # lcdi2c.lcd_clear()
    lcd.limparDisplay()
    GPIO.output(ledCompartimento[compartimento], False)
    ledAlarmeState = False
    GPIO.output(ledAlarme, ledAlarmeState)

def dispararAlarme():
    ledAlarmeState = False
    for cont in range(0, 6):
        buzzState = not buzzState
        GPIO.output(buzzer, buzzState)

        ledAlarmeState = not ledAlarmeState
        GPIO.output(ledAlarme, ledAlarmeState)
        time.sleep(1)

    time.sleep(5)
