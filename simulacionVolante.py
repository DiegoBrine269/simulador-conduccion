# Valores de ejemplo para los servos
anguloMin = 0  # Ángulo mínimo al que puede bajar un servo
anguloMax = 90  # Ángulo máximo al que puede subir un servo
limiteGiro = 45  # Límite de pulsos para el giro del volante

# Definir los servos para simulación (en tu implementación, usa los objetos reales)
class MockServo:
    def __init__(self):
        self.angle = 45  # Inicialmente en la posición central de 45 grados

servo1 = MockServo()
servo2 = MockServo()
servo3 = MockServo()
servo4 = MockServo()

# Actualizar el volante
def actualizar_volante():
    global pulsosA, pulsosB, posicionVolante, velocidad

    # Calcular la posición del volante
    posicionVolante = pulsosA - pulsosB

    # Verificar si se ha alcanzado el límite de giro
    if posicionVolante >= limiteGiro:
        print("Límite de giro hacia la derecha", end='\r', flush=True)
        posicionVolante = limiteGiro  
    elif posicionVolante <= -limiteGiro:
        print("Límite de giro hacia la izquierda", end='\r', flush=True)
        posicionVolante = -limiteGiro

    # Ajustar la sensibilidad de la vuelta en función de la velocidad
    maxVelocidad = 150  # Suponer una velocidad máxima (en la misma unidad que la variable velocidad)
    sensibilidad = 1 - min(velocidad / maxVelocidad, 1)  # Sensibilidad disminuye con la velocidad

    # Mapear la posición del volante a un ángulo de los servos proporcionalmente
    angle_range = anguloMax - anguloMin
    angle = anguloMin + (abs(posicionVolante) / limiteGiro) * angle_range * sensibilidad

    if posicionVolante > 0:  # Giro a la derecha
        servo1.angle = 45 - angle / 2  # Bajar proporcionalmente
        servo2.angle = 45 + angle / 2  # Subir proporcionalmente
        servo3.angle = 45 + angle / 2  # Subir proporcionalmente
        servo4.angle = 45 - angle / 2  # Bajar proporcionalmente
    elif posicionVolante < 0:  # Giro a la izquierda
        servo1.angle = 45 + angle / 2  # Subir proporcionalmente
        servo2.angle = 45 - angle / 2  # Bajar proporcionalmente
        servo3.angle = 45 - angle / 2  # Bajar proporcionalmente
        servo4.angle = 45 + angle / 2  # Subir proporcionalmente
    else:  # Sin giro (posición central)
        servo1.angle = 45
        servo2.angle = 45
        servo3.angle = 45
        servo4.angle = 45

    print(f"Posición Volante: {posicionVolante}, Sensibilidad: {sensibilidad}")
    print(f"Ángulo Servo Delantero Izquierdo: {servo1.angle}")
    print(f"Ángulo Servo Delantero Derecho: {servo2.angle}")
    print(f"Ángulo Servo Trasero Derecho: {servo3.angle}")
    print(f"Ángulo Servo Trasero Izquierdo: {servo4.angle}")

# Simulación de ejemplos
def simulacion():
    global pulsosA, pulsosB, velocidad

    ejemplos = [
        {"pulsosA": 1, "pulsosB": 0, "velocidad": 100},  # Pequeño giro a la derecha
        # {"pulsosA": 45, "pulsosB": 0, "velocidad": 100},  # Máximo giro a la derecha
        # {"pulsosA": 0, "pulsosB": 45, "velocidad": 100},  # Máximo giro a la izquierda
        # {"pulsosA": 22, "pulsosB": 22, "velocidad": 50},  # Sin giro
        # {"pulsosA": 40, "pulsosB": 10, "velocidad": 100}, # Giro a la derecha, alta velocidad
        # {"pulsosA": 10, "pulsosB": 40, "velocidad": 100}, # Giro a la izquierda, alta velocidad
    ]

    for ejemplo in ejemplos:
        pulsosA = ejemplo["pulsosA"]
        pulsosB = ejemplo["pulsosB"]
        velocidad = ejemplo["velocidad"]
        actualizar_volante()
        print()

# Ejecutar la simulación
simulacion()
