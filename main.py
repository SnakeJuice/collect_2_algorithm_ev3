#!/usr/bin/env pybricks-micropython
##########################################################
# Algoritmo de recolección sin obstaculos para robot EV3 #
#                                                        #
# Autores:                                               #
# - Cristian Anjari                                      #
# - Marcos Medina                                        #
#                                                        #
# Para proyecto de Tesis 2024                            #
#                                                        #
# Universidad de Santiago de Chile                       #
# Facultad de Ciencia                                    #
#                                                        #
# Licenciatura en Ciencia de la Computación/             #
# Analista en Computación Científica                     #
#                                                        #
# Santiago, Chile                                        #
# 25/03/2024                                             #
##########################################################
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.messaging import BluetoothMailboxClient, TextMailbox
import math


# Create your objects here.
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)
servo_motor = Motor(Port.C)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=140)
robot.settings(50, 50, 50, 50)

"""
    Convierte coordenadas en formato string en una lista de tuplas.
    
    Parámetros:
        string (str): El string de coordenadas convertir.
        is_obstacle (bool): Si las coordenadas representan un obstáculo.
        
    Devuelve:
        coords: Una lista de tuplas que representan las coordenadas.
"""
def string_to_coordinates(string):
    string = string[1:-1]
    parts = string.split("), (")
    coords = []
    for part in parts:
        x, y = part.split(", ")
        coords.append((int(x.strip("(")), int(y.strip(")"))))
    return coords
#################################################

"""
    Calcula la distancia Euclidiana entre dos puntos.

    Parámetros:
        point1 (tuple): El primer punto.
        point2 (tuple): El segundo punto.

    Devuelve:
        float: La distancia Euclidiana entre los dos puntos.
"""
def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
#################################################

"""
    Ordena las coordenadas de acuerdo a su posición en el plano cartesiano.
    
    Parámetros:
        coordinates (list): La lista de coordenadas a ordenar.
        
    Devuelve:
        list: La lista de coordenadas ordenadas.
"""
def sort_path(coordinates):
    coordinates.sort(key=lambda coord: (coord[1], coord[0]))
    
    '''
    # Calcula la distancia de cada coordenada al punto de inicio
    distances = [distance(start_position, coord) for coord in coordinates]

    # Selecciona la coordenada más cercana al punto de inicio
    closest_coord = coordinates[distances.index(min(distances))]

    # Usa esa coordenada como el punto de inicio para el algoritmo del viajante de comercio
    coordinates.remove(closest_coord)
    coordinates.insert(0, closest_coord)
    '''

    return coordinates
#################################################

"""
    Mueve el robot a lo largo de un camino dado.
    
    Parámetros:
        path (list): La lista de coordenadas a seguir.
        start_position (tuple): La posición inicial del robot.
        
    Devuelve:
        list: La lista de coordenadas que el robot recorrió.
        
    Nota:
        Se asume que el robot está en la posición inicial.

"""
def move_along_path(path, start_position):
    current_position = start_position
    full_path = [current_position]
    for i, (x, y) in enumerate(path):
        print("Moviendose a ",(x,y))

        # Calcula el ángulo entre la posición actual y la próxima posición
        target_angle = math.degrees(math.atan2(y - current_position[1], x - current_position[0]))
        target_angle = target_angle * -1
        
        # Calcula el ángulo relativo entre el robot y la próxima posición
        relative_angle = target_angle - current_angle

        # Gira el robot hacia el ángulo correcto
        print("Girando" ,relative_angle, "grados")
        robot.turn(relative_angle)
        
        # Actualiza el ángulo actual
        current_angle = target_angle
    
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

    return full_path
#################################################

#################################################
##----------------- main ----------------------##
#################################################

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
        path = sort_path(coordinates)
        full_path = move_along_path(path, start_position)