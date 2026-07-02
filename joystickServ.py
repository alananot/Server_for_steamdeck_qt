import socket
import threading
import RPi.GPIO as GPIO
from time import sleep
from motor_control import Car, TurretMotor
HOST = "0.0.0.0"
from buttons import shoot, lights

def joystick_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT_JOYSTICK))
    server.listen(1)
    print(f"[Joystick listening on {HOST}:{PORT_JOYSTICK}]")

    while True:
        conn, addr = server.accept()
        print(f"[Joystick] Connected to {addr}")

        while True:
            data = safe_recv(conn, 2048)
            if not data:
                break

            msg = data.decode().strip()
            values = msg.split(",")

            try:
                car_turn = int(values[0]) / -32768
                car_speed =int(values[1]) / -32768
                turret_horizontal = (int(values[2]) / -32768 + 1) * 135
                turret_vertical = (int(values[3]) / -32768 + 1) * 45
            except:
                car_turn = car_speed = turret_horizontal = turret_vertical = 0

            if get_state().lower() == "operative":

                if abs(car_speed) > 0 or abs(car_turn) > 0:
                    wheels.move(car_speed, car_turn)

                    


                if abs(turret_horizontal) > 0 or abs(turret_vertical) > 0:
                    turret.move(turret_horizontal, turret_vertical)
                
        wheels.stop() 
        turret.stop()
        conn.close()

