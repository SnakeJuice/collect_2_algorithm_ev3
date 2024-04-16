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
robot.settings(straight_speed=40, straight_acceleration=40, turn_rate=40, turn_acceleration=35)

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

def adjust_coordinates(coordinates):
    for i, (x, y) in enumerate(coordinates):
        if y == 100:
            coordinates[i] = (x - 5, y)
        if y == 80:
            coordinates[i] = (x - 10, y)
        if y == 60:
            coordinates[i] = (x - 5, y)
        if y == 40:
            coordinates[i] = (x - 5, y)
        #if y == 20:
        #    coordinates[i] = (x - 10, y)
    return coordinates

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

    return coordinates
#################################################

"""
    Calcula el ángulo relativo entre el ángulo actual y el ángulo objetivo.
    
    Parámetros:
        current_angle (float): El ángulo actual del robot.
        target_angle (float): El ángulo objetivo al que el robot quiere girar.
        
    Devuelve:
        float: El ángulo relativo que el robot necesita girar para alcanzar el ángulo objetivo.
        
    Nota:
        Esta función también agrega un extra a los grados cada vez que sean negativos o positivos.
"""
def calculate_relative_angle(current_angle, target_angle):
    # Ajusta el ángulo actual para que esté en el mismo rango que el ángulo objetivo
    #Mientras el ángulo actual - el ángulo objetivo sea mayor a 180
    while current_angle - target_angle > 180:
        #Resta 360 al ángulo actual
        current_angle -= 360
    #Mientras el ángulo actual - el ángulo objetivo sea menor a -180
    while current_angle - target_angle < -180:
        #Suma 360 al ángulo actual
        current_angle += 360

    relative_angle = target_angle - current_angle

    
    # Agrega un extra a los grados cada vez que sean negativos o positivos
    extra = 7 # Define el extra que quieres agregar
    threshold = 0.01  # Define el umbral

    # Si el ángulo relativo es mayor al umbral, agrega el extra
    if abs(relative_angle) > threshold:
        # Si el ángulo relativo es negativo, agrega el extra
        if relative_angle < 0:
            # Se le quita el extra a los grados
            relative_angle -= extra
        # Si el ángulo relativo es positivo, agrega el extra
        elif relative_angle > 0:
            # Se le quita el extra a los grados 
            relative_angle += extra
    

    return relative_angle
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
    current_angle = robot.angle()
    current_position = start_position
    full_path = [current_position]
    extra_distance = 50 # 5cm

    for i, (x, y) in enumerate(path):
        print("Moviendose a ",(x,y))

        # Calcula el ángulo entre la posición actual y la próxima posición
        angle = -(math.degrees(math.atan2(y - current_position[1], x - current_position[0])))
        
        relative_angle = calculate_relative_angle(current_angle, angle)
        
        # Agrega un extra a los grados cada vez que sean negativos o positivos
        print("Relative_angle ", relative_angle)
        
        #relative_angle = math.floor(relative_angle)
        print("Girando " ,relative_angle, "grados")
        robot.turn(relative_angle)
        wait(10000)
        ev3.speaker.beep()

        current_angle = angle
        
        # Calcula la distancia a moverse en milímetros
        distance = math.sqrt((x - current_position[0])**2 + (y - current_position[1])**2) * 10  # cada unidad es mm
        
        # Si el robot está cambiando de fila, agrega una distancia extra
        if current_position[1] != y:
            distance += extra_distance
        
        # Mueve el robot a la posición (x, y)
        print("Moviendose ",distance, " mm")
        servo_motor.run_angle(150,50)
        
        robot.straight(distance)
            
        servo_motor.run_angle(150,-50)
        
        # Actualiza la posición actual
        current_position = (x, y)
        full_path.append(current_position)
        
        print("Llegó a la posición ", (x,y))

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
        robot.reset()
        start_position = (-19,40)
        coordinates = string_to_coordinates(verdes)
        coordinates = adjust_coordinates(coordinates)
        print(coordinates)
        path = sort_path(coordinates)
        full_path = move_along_path(path, start_position)