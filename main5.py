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
servo1 = servo.Servo(pca.channels[0])
servo2 = servo.Servo(pca.channels[1])
servo3 = servo.Servo(pca.channels[2])
servo4 = servo.Servo(pca.channels[3])

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
    servo1.angle = 67.5
    servo2.angle = 67.5
    servo3.angle = 67.5
    servo4.angle = 67.5


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

            
        print(f"---- Velocidad actual: {velocidad:.2f} m/s Giro: ", giro, "PulsosA: ", pulsosA, "PulsosB: ", pulsosB,  "Clutch: ", clutch, "Freno: ", freno,"Acelerador: ", acelerador, "Transmisión: ", transmision, "-----",  end='\r', flush=True)


def funcionamiento () :

    global acelerador, freno, clutch, transmision, velocidad

    # Rango de velocidades máximas por marcha (en m/s)
    velocidadesMaximas = [0, 20, 40, 60, 80, 90, -10]  # La última es para reversa

    # Coeficientes de aceleración por marcha
    coeficientesAceleracion = [0, 5, 4, 3, 2, 1, 2]  # La última es para reversa

    while True:
        # Constantes de desaceleración
        maxFrenado = 15  # m/s^2 para freno al 100%
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
        velocidad = nuevaVelocidad

        sleep(1)


def listener():
    global transmision

    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x=0

    while True:
        x = sys.stdin.read(1)[0]
        
        if x in '0123456':
            transmision = int(x)
    
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)



if __name__ == "__main__":
    main()
    


    
