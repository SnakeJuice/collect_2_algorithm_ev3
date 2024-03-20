#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.messaging import BluetoothMailboxClient, TextMailbox

import math

#import itertools

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)
servo_motor = Motor(Port.C)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=140)
robot.settings(50, 50, 50, 50)


def string_to_coordinates(string):
    string = string[1:-1]
    parts = string.split("), (")
    coords = []
    for part in parts:
        x, y = part.split(", ")
        coords.append((int(x.strip("(")), int(y.strip(")"))))
    return coords

#Mejor heuristica para movimientos en 4 direcciones
def distance(point1, point2):
    # Calcula la distancia de Manhattan entre dos puntos
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

#Traveling Salesman Problem - Brute Force
#Complejidad factorial! O(n!)
def calculate_optimal_path(coordinates, start_position):
    # Calcula la distancia de cada coordenada al punto de inicio
    distances = [distance(start_position, coord) for coord in coordinates]

    # Selecciona la coordenada más cercana al punto de inicio
    closest_coord = coordinates[distances.index(min(distances))]

    # Usa esa coordenada como el punto de inicio para el algoritmo del viajante de comercio
    coordinates.remove(closest_coord)
    coordinates.insert(0, closest_coord)

    # Genera todas las permutaciones posibles de las coordenadas
    permutations = generate_permutations(coordinates)

    # Calcula la longitud total de cada permutación
    lengths = [sum(distance(point1, point2) for point1, point2 in zip(permutation[:-1], permutation[1:])) for permutation in permutations]

    # Encuentra la permutación con la longitud más corta
    shortest_permutation = permutations[lengths.index(min(lengths))]

    return shortest_permutation

def generate_permutations(lst):
    if len(lst) == 0:
        return [[]]
    permutations = []
    for i in range(len(lst)):
        sub_permutations = generate_permutations(lst[:i] + lst[i+1:])
        for perm in sub_permutations:
            permutations.append([lst[i]] + perm)
    return permutations

def move_along_path(path, start_position):
    current_position = start_position
    full_path = [current_position]
    for i, (x, y) in enumerate(path):
        print("Moviendose a ",(x,y))

        # Calcula el ángulo entre la posición actual y la próxima posición
        angle = math.degrees(math.atan2(y - current_position[1], x - current_position[0]))

        # Gira el robot hacia el ángulo correcto
        #robot.turn(angle)
        print("Girando" ,angle, "grados")
        robot.turn(angle)
    
        # Calcula la distancia a moverse en milímetros
        distance = math.sqrt((x - current_position[0])**2 + (y - current_position[1])**2) * 10  # cada unidad es mm
        # Mueve el robot a la posición (x, y)
        #robot.straight(distance)
        print("Moviendose",distance, " mm")
        servo_motor.run_angle(150,90)
        robot.straight(distance)
        servo_motor.run_angle(150,-90)
        # Actualiza la posición actual
        current_position = (x, y)
        full_path.append(current_position)
        
        print("Llegó a la posición", (x,y))

        # Si es el último punto, vuelve al inicio
        '''if i == len(path) - 1:
            print("Volviendo al inicio ({start_position[0]},{start_position[1]})")
            # Calcula el ángulo y la distancia al punto de inicio
            angle = math.degrees(math.atan2(start_position[1] - y, start_position[0] - x))
            distance = math.sqrt((start_position[0] - x)**2 + (start_position[1] - y)**2) * 10
            # Gira el robot hacia el ángulo correcto
            #robot.turn(angle)
            print("Girando {angle} grados")
            robot.turn(angle)
            # Mueve el robot al punto de inicio
            print("Moviendose {distance} mm")
            robot.straight(distance)
            #full_path.append(start_position)'''

    return full_path

SERVER = 'Master'

client = BluetoothMailboxClient()

rbox2 = TextMailbox('rec2', client)

print('establishing connection...')
client.connect(SERVER)
ev3.screen.print('connected!')

while True:
    rbox2.send('Recolector2 conectado')
    rbox2.wait()
    #rbox.read()
    print("rbox2.read ",rbox2.read())
    if(rbox2.read()[0] == '['):
        verdes = rbox2.read()
        ev3.screen.print("lista verde",verdes)
    rbox2.send('ok verdes') 
    rbox2.wait_new()   
    if(rbox2.read()=='inicia'):
        #robot.straight(100)
        start_position = (0,17)
        verdes = [(33, 17), (60, 34)]
        coordinates = string_to_coordinates(verdes)
        print(coordinates)
        path = calculate_optimal_path(coordinates, start_position)
        full_path = move_along_path(path, start_position)
