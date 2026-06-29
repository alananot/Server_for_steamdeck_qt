import socket
import threading
import RPi.GPIO as GPIO
from motor_control import CarMotor, TurretMotor
from time import sleep
from buttons import shoot
HOST = "0.0.0.0"
PORT_HUD = 2222
PORT_GRAPH = 2223
PORT_BUTTONS = 2224
PORT_JOYSTICK = 2225



PIN = 17



state_lock = threading.Lock()
state = "Connect"


def set_state(new_state):
    global state
    with state_lock:
        state = new_state


def get_state():
    with state_lock:
        return state


def safe_recv(conn, size):
    try:
        return conn.recv(size)
    except socket.timeout:
        return None
    except ConnectionResetError:
        return None


def hud_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT_HUD))
    server.listen(1)
    print(f"[HUD listening on {HOST}:{PORT_HUD}]")

    while True:
        conn, addr = server.accept()
        conn.settimeout(2)
        print(f"[HUD] Connected to {addr}")

        while True:
            data = safe_recv(conn, 1024)
            if not data:
                break

            new_state = data.decode().strip()
            set_state(new_state)

            #print("Current:", new_state)
            conn.sendall(b'ACK')

            if new_state == "idle":
                break

        conn.close()


def graph_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT_GRAPH))
    server.listen(1)
    print(f"[GRAPH listening on {HOST}:{PORT_GRAPH}]")

    while True:
        conn, addr = server.accept()
        conn.settimeout(2)
        print(f"[GRAPH] Connected to {addr}")

        while True:
            data = safe_recv(conn, 1024)
            if not data:
                break

            value = GPIO.input(PIN)
            
            if(value == 1):
                GPIO.output(PIN, GPIO.LOW)
            else:
                GPIO.output(PIN,GPIO.HIGH)

            conn.sendall(str(value).encode())

        conn.close()


def buttons_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT_BUTTONS))
    server.listen(1)
    print(f"[BUTTONS listening on {HOST}:{PORT_BUTTONS}]")

    while True:
        conn, addr = server.accept()
        conn.settimeout(2)
        print(f"[BUTTONS] Connected to {addr}")

        while True:
            data = safe_recv(conn, 1024)
            if not data:
                break
            
            msg = data.decode().strip()
            buttons = msg.split(",")
            a = buttons[0]
            print(a)
            if get_state() == "Operative":
                break

        conn.close()


def joystick_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT_JOYSTICK))
    server.listen(1)
    print(f"[Joystick listening on {HOST}:{PORT_JOYSTICK}]")

    while True:
        conn, addr = server.accept()
        conn.settimeout(2)
        print(f"[Joystick] Connected to {addr}")

        while True:
            data = safe_recv(conn, 2048)
            if not data:
                break

            msg = data.decode().strip()
            values = msg.split(",")

            car_turn = int(values[0])
            car_speed = int(values[1])
            turret_horizontal = int(values[2])
            turret_vertical = int(values[3])

            if get_state().lower() == "operative":
                if abs(car_speed) > 0 or abs(car_turn) > 0:
                    wheels.car_move(car_speed / 32768, car_turn / 32768)
                else:
                    wheels.stop()

                if abs(turret_horizontal) > 0 or abs(turret_vertical) > 0:
                    turret_horizontal /= 32768
                    turret_vertical /= 32768
                    turret.turret_move(turret_horizontal,turret_vertical)

        conn.close()


# Start servers
threading.Thread(target=hud_server, daemon=True).start()
threading.Thread(target=graph_server, daemon=True).start()
threading.Thread(target=buttons_server, daemon=True).start()
threading.Thread(target=joystick_server, daemon=True).start()
wheels = CarMotor(11, 13, 15, 29, 31, 33)
turret = TurretMotor(8, 10, 12, 16, 18, 22)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

while True:
    sleep(0.1)
