import socket
import time
import serial
from time import sleep
from funciones import acondicionarPedal
import RPi.GPIO as GPIO
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

ser = serial.Serial(
    port='/dev/ttyS0', 
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)



i2c = board.I2C()  
pca = PCA9685(i2c)
pca.frequency = 50
servo1 = servo.Servo(pca.channels[0])
servo2 = servo.Servo(pca.channels[1])
servo3 = servo.Servo(pca.channels[2])
servo4 = servo.Servo(pca.channels[3])

velocidad = 0

# Banderas
acelerando = False
frenando = False

tiempoTranscurrido = 0
tiempoTemp = 0



# Mapeo de pines
    # Pin GPIO23 - Delantera izquierda
    # Pin GPIO17 - Delantera derecha
    # Pin GPIO22 - Trasera derecha 
    # Pin GPIO27 - Trasera izquierda


def main():

    servo1.angle = 67.5
    servo2.angle = 67.5
    servo3.angle = 67.5
    servo4.angle = 67.5

    lectura()

def acelerar():
    servo3.angle = 0
    servo4.angle = 0
    servo1.angle = 135
    servo2.angle = 135

def frenar():
    servo1.angle = 0
    servo2.angle = 0
    servo3.angle = 135
    servo4.angle = 135 

    
def lectura():

    # Indica si se está girando a la izquierda (I), o derecha (D)
    giro = ''

    pulsosA = 0
    pulsosB = 0

    # Variables de pedales (0 - 100)
    clutch = 0
    freno = 0
    acelerador = 0

    transmision = 0

    switch = 0 

    tiempoFrenando = 0
    tiempoAcelerando = 0

    while True:
        lectura = ser.read()

        # Detectando Identificador, para leer el siguiente dato
        if lectura == b'G':
            giro = ser.read()
            if giro== b'D' :
                pulsosA += 1
            elif giro == b'I' :
                pulsosB += 1

        elif lectura == b'A':
            aceleradorInf = int.from_bytes(ser.read(), byteorder='big')
            aceleradorSup = int.from_bytes(ser.read(), byteorder='big') << 8
            acelerador = acondicionarPedal(aceleradorSup, aceleradorInf)
            if acelerador > 10:
                tiempoAcelerando +=1

            if tiempoAcelerando > 10:
                tiempoAcelerando = 0
                acelerar()
            
        elif lectura == b'F':
            freno = ser.read()
            frenoInf = int.from_bytes(freno, byteorder='big')
            freno = ser.read()
            frenoSup = int.from_bytes(freno, byteorder='big') << 8
            freno = acondicionarPedal(frenoSup, frenoInf)

            if freno > 10:
                tiempoFrenando +=1

            if tiempoFrenando > 10:
                tiempoFrenando = 0
                frenar()

        elif lectura == b'C':
            clutch = ser.read()
            clutchInf = int.from_bytes(clutch, byteorder='big')
            clutch = ser.read()
            clutchSup = int.from_bytes(clutch, byteorder='big') << 8
            clutch = acondicionarPedal(clutchSup, clutchInf)

        elif lectura == b'T':
            transmision = ser.read()
            
        elif lectura == b'S':
            switch = ser.read()
            
        print("Giro: ", giro, "PulsosA: ", pulsosA, "PulsosB: ", pulsosB,  "Clutch: ", clutch, "Freno: ", freno,"Acelerador: ", acelerador, "Angulo: ", end='\r', flush=True)

# Función que incrementa el contador de tiempo cada segundo
def contador_tiempo():
    global tiempoTranscurrido
    while True:
        tiempoTranscurrido += 1
        time.sleep(1)



if __name__ == "__main__":
    main()
    


    
