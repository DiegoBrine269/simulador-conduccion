# Valores de ejemplo para los servos
angulo_min_servo = 30  # Ángulo mínimo al que puede bajar un servo
angulo_max_servo = 60  # Ángulo máximo al que puede subir un servo
limiteGiro = 45  # Límite de pulsos para el giro del volante

# Definir los servos para simulación (en tu implementación, usa los objetos reales)
class MockServo:
    def __init__(self):
        self.angle = 0

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

    # Mapear la posición del volante a un ángulo de los servos
    if posicionVolante > 0 and velocidad != 0:  # Giro a la derecha
        servo1.angle = angulo_max_servo * sensibilidad  # Subir
        servo2.angle = angulo_min_servo + ((posicionVolante / limiteGiro) * (angulo_max_servo - angulo_min_servo) / 2) * sensibilidad  # Bajar parcialmente
        servo3.angle = angulo_min_servo + ((posicionVolante / limiteGiro) * (angulo_max_servo - angulo_min_servo) / 2) * sensibilidad  # Bajar parcialmente
        servo4.angle = angulo_max_servo * sensibilidad  # Subir
    elif posicionVolante < 0 and velocidad != 0:  # Giro a la izquierda
        servo1.angle = angulo_min_servo + ((-posicionVolante / limiteGiro) * (angulo_max_servo - angulo_min_servo) / 2) * sensibilidad  # Bajar parcialmente
        servo2.angle = angulo_max_servo * sensibilidad  # Subir
        servo3.angle = angulo_max_servo * sensibilidad  # Subir
        servo4.angle = angulo_min_servo + ((-posicionVolante / limiteGiro) * (angulo_max_servo - angulo_min_servo) / 2) * sensibilidad  # Bajar parcialmente
    else:  # Sin giro (posición central)
        servo1.angle = (angulo_max_servo + angulo_min_servo) / 2
        servo2.angle = (angulo_max_servo + angulo_min_servo) / 2
        servo3.angle = (angulo_max_servo + angulo_min_servo) / 2
        servo4.angle = (angulo_max_servo + angulo_min_servo) / 2

    print(f"Posición Volante: {posicionVolante}, Sensibilidad: {sensibilidad}")
    print(f"Ángulo Servo Delantero Izquierdo: {servo1.angle}")
    print(f"Ángulo Servo Delantero Derecho: {servo2.angle}")
    print(f"Ángulo Servo Trasero Derecho: {servo3.angle}")
    print(f"Ángulo Servo Trasero Izquierdo: {servo4.angle}")

# Simulación de ejemplos
def simulacion():
    global pulsosA, pulsosB, velocidad

    ejemplos = [
        {"pulsosA": 0, "pulsosB": 0, "velocidad":0},  # Giro a la derecha
        # {"pulsosA": 10, "pulsosB": 30, "velocidad": 50},  # Giro a la izquierda
        # {"pulsosA": 20, "pulsosB": 20, "velocidad": 50},  # Sin giro
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
