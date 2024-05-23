import threading
import time
import serial
from time import sleep
from funciones import acondicionarPedal
import RPi.GPIO as GPIO
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import tty, sys, termios

ser = serial.Serial(
    port='/dev/ttyUSB0', 
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

i2c = board.I2C()  
pca = PCA9685(i2c)
pca.frequency = 50

servo1 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2400, actuation_range=90)
servo2 = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2400, actuation_range=90)
servo3 = servo.Servo(pca.channels[2], min_pulse=500, max_pulse=2400, actuation_range=90)
servo4 = servo.Servo(pca.channels[3], min_pulse=500, max_pulse=2400, actuation_range=90)

acelerador = 0
freno = 0
clutch = 0
transmision = 0
velocidad = 0
giro = ''
pulsosA = 0
pulsosB = 0

def main():
    # Inicializando pistones
    servo1.angle = 45
    servo2.angle = 45
    servo3.angle = 45
    servo4.angle = 45

    p1 = threading.Thread(target=lectura)
    p2 = threading.Thread(target=funcionamiento)
    p3 = threading.Thread(target=listener)
    p3.start()
    p1.start()
    p2.start()


def lectura():

    global acelerador, freno, clutch, transmision, velocidad, giro, pulsosA, pulsosB

    while True:

        lectura = ser.read()

        # Detectando Identificador, para leer el siguiente dato
        if lectura == b'G':
            
            giro = ser.read()
            if giro == b'D' :
                pulsosA += 1
            elif giro == b'I' :
                pulsosB += 1

        elif lectura == b'A':
            aceleradorInf = int.from_bytes(ser.read(), byteorder='big')
            aceleradorSup = int.from_bytes(ser.read(), byteorder='big') << 8
            acelerador = acondicionarPedal(aceleradorSup, aceleradorInf)

            
        elif lectura == b'F':
            frenoInf = int.from_bytes(ser.read(), byteorder='big')
            frenoSup = int.from_bytes(ser.read(), byteorder='big') << 8
            freno = acondicionarPedal(frenoSup, frenoInf)


        elif lectura == b'C':
            clutchInf = int.from_bytes(ser.read(), byteorder='big')
            clutchSup = int.from_bytes(ser.read(), byteorder='big') << 8
            clutch = acondicionarPedal(clutchSup, clutchInf)

            
        print(f"---- Velocidad actual: {velocidad:.2f} km/h Giro: ", giro, "PulsosA: ", pulsosA, "PulsosB: ", pulsosB,  "Clutch: ", clutch, "Freno: ", freno,"Acelerador: ", acelerador, "Transmisión: ", transmision, "-----",  end='\r', flush=True)


def funcionamiento () :

    global acelerador, freno, clutch, transmision, velocidad

    # Rango de velocidades máximas por marcha (en m/s)
    velocidadesMaximas = [150, 20, 40, 60, 80, 164, -10]  # La última es para reversa

    # Coeficientes de aceleración por marcha
    coeficientesAceleracion = [0, 7, 6, 5, 3, 1, 2]  # La última es para reversa

    while True:
        # Constantes de desaceleración
        maxFrenado = 10  # m/s^2 para freno al 100%
        resistencia = 0.1  # Resistencia al movimiento

        if transmision == 0 or clutch > 50:  # Neutral o clutch muy presionado
            aceleracionEfectiva = 0
        else:
            # Coeficiente de la marcha actual
            coeficiente = coeficientesAceleracion[transmision]
            
            # Aceleración efectiva basada en la transmisión y el acelerador
            aceleracionEfectiva = (acelerador / 100) * coeficiente

        # Desaceleración efectiva basada en el freno
        frenadoEfectivo = (freno / 100) * maxFrenado

        # Ajuste de la velocidad
        nuevaVelocidad = velocidad + aceleracionEfectiva - frenadoEfectivo - resistencia

        # Limitar la velocidad máxima de acuerdo a la marcha
        velocidadMaxima = velocidadesMaximas[transmision]
        if transmision != 6 and nuevaVelocidad > velocidadMaxima:  # No limitar la reversa
            nuevaVelocidad = velocidadMaxima
        elif transmision == 6 and nuevaVelocidad < velocidadMaxima:
            nuevaVelocidad = velocidadMaxima

        # Asegurarse de que la velocidad no sea negativa (excepto en reversa)
        if transmision != 6 and nuevaVelocidad < 0:
            nuevaVelocidad = 0

        actualizarPosicion(nuevaVelocidad - velocidad)

        velocidad = nuevaVelocidad

        sleep(1)


def listener():
    global transmision, clutch

    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x=0

    while True:
        x = sys.stdin.read(1)[0]
        
        if x in '0123456':
            if clutch > 50:
                transmision = int(x)
    
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

# Actualiza la posición de los pistones en función a un cambio en la velocidad
def actualizarPosicion(aceleracion):
    # Aceleraciones positivas

    if aceleracion >= 4:
        servo1.angle = 70
        servo2.angle = 70
        servo3.angle = 20
        servo4.angle = 20
    elif aceleracion >= 3:
        servo1.angle = 60
        servo2.angle = 60
        servo3.angle = 30
        servo4.angle = 30
    elif aceleracion >= 2:
        servo1.angle = 55
        servo2.angle = 55
        servo3.angle = 35
        servo4.angle = 35
    elif aceleracion >= 1:
        servo1.angle = 50
        servo2.angle = 50
        servo3.angle = 40
        servo4.angle = 40

    # Sin cambio en la velocidad
    elif (aceleracion >= 0 and aceleracion < 1) or (aceleracion <= 0 and aceleracion > -1):
        servo1.angle = 45
        servo2.angle = 45
        servo3.angle = 45
        servo4.angle = 45

    # Acelereaciones negativas

    elif aceleracion <= -1:
        servo1.angle = 40
        servo2.angle = 40
        servo3.angle = 50
        servo4.angle = 50
    elif aceleracion <= -5:
        servo1.angle = 30
        servo2.angle = 30
        servo3.angle = 60
        servo4.angle = 60
    if aceleracion <= -8:
        servo1.angle = 10
        servo2.angle = 10
        servo3.angle = 80
        servo4.angle = 80



if __name__ == "__main__":
    main()
    


    
