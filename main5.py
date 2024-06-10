import threading
import time
import serial
from time import sleep
from funciones import acondicionarPedal
import digitalio
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

# Pines de la llave
llave = ""

llave0 = digitalio.DigitalInOut(board.D16)
llave0.direction = digitalio.Direction.INPUT
llave0.pull = digitalio.Pull.UP  # Activar resistencia pull-up interna

llave1 = digitalio.DigitalInOut(board.D20)
llave1.direction = digitalio.Direction.INPUT
llave1.pull = digitalio.Pull.UP  # Activar resistencia pull-up interna

llave2 = digitalio.DigitalInOut(board.D21)
llave2.direction = digitalio.Direction.INPUT
llave2.pull = digitalio.Pull.UP  # Activar resistencia pull-up interna

led = digitalio.DigitalInOut(board.D12)
led.direction = digitalio.Direction.OUTPUT

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
    servo1.angle = 60
    servo2.angle = 60
    servo3.angle = 60
    servo4.angle = 60

    p1 = threading.Thread(target=lectura)
    p2 = threading.Thread(target=funcionamiento)
    p3 = threading.Thread(target=listener)
    p3.start()
    p1.start()
    p2.start()

def lectura():
    global acelerador, freno, clutch, transmision, velocidad, giro, pulsosA, pulsosB, posicionVolante, limiteGiro, llave

    while True:
        
        # Lectura de llave
        llave = f"{int(llave2.value)}{int(llave1.value)}{int(llave0.value)}"

 
        lectura = ser.read()

        # Detectando Identificador, para leer el siguiente dato
        if lectura == b'G':
            giro = ser.read()
            if giro == b'D':
                pulsosA += 1
            elif giro == b'I':
                pulsosB += 1

            # Calcular la posición del volante
            posicionVolante = pulsosA - pulsosB

            # Verificar si se ha alcanzado el límite de giro
            if posicionVolante >= limiteGiro:
                posicionVolante = limiteGiro  
            elif posicionVolante <= -limiteGiro:
                posicionVolante = -limiteGiro  # Limitar la posición del volante

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

        if llave == "000" or llave == "100" or llave == "010" :
            estado = "Apagado"
        else :
            estado = "Encendido"

        print(f"---- Velocidad actual: {velocidad:.2f} km/h Giro: {giro} PulsosA: {pulsosA} PulsosB: {pulsosB} Clutch: {clutch} Freno: {freno} Acelerador: {acelerador} Transmisión: {transmision}, Volante: {posicionVolante}, Estado {estado} -----", end='\r', flush=True)

def funcionamiento():
    global acelerador, freno, clutch, transmision, velocidad, posicionVolante, llave

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

            if(acelerador < 10):
                resistencia = 1

        # Desaceleración efectiva basada en el freno
        frenadoEfectivo = (freno / 100) * maxFrenado

        # Ajuste de la velocidad
        if llave == "000" or llave == "100" or llave == "010":
            aceleracionEfectiva = 0

        nuevaVelocidad = velocidad + aceleracionEfectiva - frenadoEfectivo - resistencia

        # Limitar la velocidad máxima de acuerdo a la marcha
        velocidadMaxima = velocidadesMaximas[transmision]
        if transmision != 6:  # No limitar la reversa
            if nuevaVelocidad > velocidadMaxima :
                nuevaVelocidad = velocidadMaxima
                led.value = True
            else:
                led.value = False
                
        elif transmision == 6 and nuevaVelocidad < velocidadMaxima:
            nuevaVelocidad = velocidadMaxima

        # Asegurarse de que la velocidad no sea negativa (excepto en reversa)
        if transmision != 6 and nuevaVelocidad < 0:
            nuevaVelocidad = 0

        actualizarPosicion(nuevaVelocidad - velocidad, posicionVolante, velocidad)

        velocidad = nuevaVelocidad

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
def actualizarPosicion(aceleracion, posicionVolante, velocidad):

    angles = (45, 45, 45, 45)

    if velocidad == 0:
        angles = (45, 45, 45, 45)
    else:
        if posicionVolante > -3 and posicionVolante < 3:
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
                angles = (20, 20, 80, 80)
            else:
                angles = (10, 10, 80, 80)

        #Giros a la izquierda
        elif -20 < posicionVolante <= -4:
            if velocidad < 10:
                angles = (45, 35, 35, 45)
            elif 10 < velocidad < 40: 
                angles = (45, 25, 25, 45)
            elif 41 <= velocidad :
                angles = (45, 15, 15, 45)
        elif -45 <= posicionVolante  <= -21:
            if velocidad < 10:
                angles = (45, 25, 25, 45)
            elif 10 < velocidad < 40:
                angles = (45, 15, 15, 45)
            elif 41 <= velocidad :
                angles = (10, 60, 60, 10)

        # Giros a la derecha
        elif 4 <= posicionVolante < 20:
            if velocidad < 10:
                angles = (30, 45, 45, 30)
            elif 10 <= velocidad < 40:
                angles = (25, 45, 45, 25)
            elif 41 <= velocidad :
                angles = (15, 45, 45, 15)
        elif 21 <= posicionVolante <= 45:
            if velocidad < 10:
                angles = (15, 55, 55, 15)
            elif 10 <= velocidad < 40:
                angles = (10, 60, 60, 10)
            elif 41 <= velocidad :
                angles = (80,10, 10, 80)
    
    servo1.angle, servo2.angle, servo3.angle, servo4.angle = angles



if __name__ == "__main__":
    main()