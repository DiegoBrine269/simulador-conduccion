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

# Variables globales existentes
acelerador = 0
freno = 0
clutch = 0
transmision = 0
velocidad = 0
giro = ''
pulsosA = 0
pulsosB = 0

# Nueva variable global para la posición del volante
posicionVolante = 0
anguloMin = 0
anguloMax = 90

# Definir los límites de giro del volante
limiteGiro = 45  # 1.5 vueltas son 45 posiciones

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
            if giro == b'D':
                pulsosA += 1
            elif giro == b'I':
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

        print(f"---- Velocidad actual: {velocidad:.2f} km/h Giro: {giro} PulsosA: {pulsosA} PulsosB: {pulsosB} Clutch: {clutch} Freno: {freno} Acelerador: {acelerador} Transmisión: {transmision} -----", end='\r', flush=True)

def funcionamiento():
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

        # Actualizar el volante
        actualizar_volante()

        sleep(1)

def listener():
    global transmision, clutch

    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x = 0

    while True:
        x = sys.stdin.read(1)[0]

        if x in '0123456':
            if clutch > 50:
                transmision = int(x)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

# Actualiza la posición de los pistones en función a un cambio en la velocidad
def actualizarPosicion(aceleracion):
    if aceleracion >= 4:
        angles = (70, 70, 20, 20)
    elif aceleracion >= 3:
        angles = (60, 60, 30, 30)
    elif aceleracion >= 2:
        angles = (55, 55, 35, 35)
    elif aceleracion >= 1:
        angles = (50, 50, 40, 40)
    elif -1 < aceleracion < 1:
        angles = (45, 45, 45, 45)
    elif aceleracion >= -5:
        angles = (40, 40, 50, 50)
    elif aceleracion >= -8:
        angles = (30, 30, 60, 60)
    else:
        angles = (10, 10, 80, 80)

    servo1.angle, servo2.angle, servo3.angle, servo4.angle = angles

# Actualizar el volante
def actualizar_volante():
    global pulsosA, pulsosB, posicionVolante, velocidad

    # Calcular la posición del volante
    posicionVolante = pulsosA - pulsosB

    # Verificar si se ha alcanzado el límite de giro
    if posicionVolante >= limiteGiro:
        print("Advertencia: Se ha alcanzado el límite de giro hacia la derecha", end='\r', flush=True)
        posicionVolante = limiteGiro  # Limitar la posición del volante
    elif posicionVolante <= -limiteGiro:
        print("Advertencia: Se ha alcanzado el límite de giro hacia la izquierda", end='\r', flush=True)
        posicionVolante = -limiteGiro  # Limitar la posición del volante

    # Ajustar la sensibilidad de la vuelta en función de la velocidad
    maxVelocidad = 150  # Suponer una velocidad máxima (en la misma unidad que la variable velocidad)
    sensibilidad = 1 - min(velocidad / maxVelocidad, 1)  # Sensibilidad disminuye con la velocidad

    # Mapear la posición del volante a un ángulo de los servos
    if posicionVolante > 0:  # Giro a la derecha
        servo1.angle = anguloMax * sensibilidad  # Subir
        servo2.angle = anguloMin + ((posicionVolante / limiteGiro) * (anguloMax - anguloMin) / 2) * sensibilidad  # Bajar parcialmente
        servo3.angle = anguloMin + ((posicionVolante / limiteGiro) * (anguloMax - anguloMin) / 2) * sensibilidad  # Bajar parcialmente
        servo4.angle = anguloMax * sensibilidad  # Subir
    elif posicionVolante < 0:  # Giro a la izquierda
        servo1.angle = anguloMin + ((-posicionVolante / limiteGiro) * (anguloMax - anguloMin) / 2) * sensibilidad  # Bajar parcialmente
        servo2.angle = anguloMax * sensibilidad  # Subir
        servo3.angle = anguloMax * sensibilidad  # Subir
        servo4.angle = anguloMin + ((-posicionVolante / limiteGiro) * (anguloMax - anguloMin) / 2) * sensibilidad  # Bajar parcialmente
    else:  # Sin giro (posición central)
        servo1.angle = (anguloMax + anguloMin) / 2
        servo2.angle = (anguloMax + anguloMin) / 2
        servo3.angle = (anguloMax + anguloMin) / 2
        servo4.angle = (anguloMax + anguloMin) / 2

    print(f"Posición Volante: {posicionVolante}, Sensibilidad: {sensibilidad}")
    print(f"Ángulo Servo Delantero Izquierdo: {servo1.angle}")
    print(f"Ángulo Servo Delantero Derecho: {servo2.angle}")
    print(f"Ángulo Servo Trasero Derecho: {servo3.angle}")
    print(f"Ángulo Servo Trasero Izquierdo: {servo4.angle}")


if __name__ == "__main__":
    main()
