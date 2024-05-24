def acondicionarPedal (pedalSup, pedalInf):
    pedal = pedalSup + pedalInf
    pedal -= 150    
    pedal /= 7.3
    pedal = int(pedal)

    if pedal <= 5:
        pedal = 0
    elif pedal > 100:
        pedal = 100

    return pedal
