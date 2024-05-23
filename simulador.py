import threading
import time

# Variables globales
acelerador = 0
freno = 0
clutch = 0
transmision = 0

# Variables del estado del carro
velocidad = 0.0

# Rango de velocidades máximas por marcha (en m/s)
velocidades_maximas = [0, 15, 30, 45, 60, 75, -10]  # La última es para reversa

# Coeficientes de aceleración por marcha
coeficientes_aceleracion = [0, 5, 4, 3, 2, 1, 2]  # La última es para reversa

def calcular_velocidad():
    global velocidad, acelerador, freno, clutch, transmision

    # Constantes de desaceleración
    max_frenado = 15  # m/s^2 para freno al 100%
    resistencia = 0.1  # Resistencia al movimiento

    if transmision == 0 or clutch > 50:  # Neutral o clutch muy presionado
        aceleracion_efectiva = 0
    else:
        # Coeficiente de la marcha actual
        coeficiente = coeficientes_aceleracion[transmision]
        
        # Aceleración efectiva basada en la transmisión y el acelerador
        aceleracion_efectiva = (acelerador / 100) * coeficiente

    # Desaceleración efectiva basada en el freno
    frenado_efectivo = (freno / 100) * max_frenado

    # Ajuste de la velocidad
    nueva_velocidad = velocidad + aceleracion_efectiva - frenado_efectivo - resistencia

    # Limitar la velocidad máxima de acuerdo a la marcha
    velocidad_maxima = velocidades_maximas[transmision]
    if transmision != 6 and nueva_velocidad > velocidad_maxima:  # No limitar la reversa
        nueva_velocidad = velocidad_maxima
    elif transmision == 6 and nueva_velocidad < velocidad_maxima:
        nueva_velocidad = velocidad_maxima

    # Asegurarse de que la velocidad no sea negativa (excepto en reversa)
    if transmision != 6 and nueva_velocidad < 0:
        nueva_velocidad = 0

    velocidad = nueva_velocidad
    print(f"Velocidad actual: {velocidad:.2f} m/s, Transmisión: {transmision}, Acelerador: {acelerador}, Freno: {freno}")

def ejecutar_cada_segundo():
    calcular_velocidad()
    threading.Timer(1, ejecutar_cada_segundo).start()

# Inicializa la ejecución periódica
ejecutar_cada_segundo()

# Simulación de cambios en las variables (esto sería controlado por el usuario o por otro código)
try:
    while True:
        time.sleep(3)
        # Simulación de cambios en los controles
        acelerador = 50
        freno = 0
        clutch = 0
        transmision = 1

        time.sleep(4)
        acelerador = 100
        freno = 0
        clutch = 0
        transmision = 2

        time.sleep(5)
        acelerador = 100
        freno = 0
        clutch = 0
        transmision = 3

        time.sleep(5)
        acelerador = 100
        freno = 0
        clutch = 0
        transmision = 4

        time.sleep(5)
        acelerador = 0
        freno = 50
        clutch = 0
        transmision = 3

        time.sleep(5)
        acelerador = 0
        freno = 50
        clutch = 0
        transmision = 1

        time.sleep(6)
        acelerador = 0
        freno = 0
        clutch = 0
        transmision = 6  # Reversa
        time.sleep(10)
        acelerador = 50
        freno = 0
        clutch = 0
        transmision = 6  # Reversa

except KeyboardInterrupt:
    print("Simulación terminada.")
