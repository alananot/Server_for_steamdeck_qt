import socket
import threading
import RPi.GPIO as GPIO
from time import sleep
from motor_control import Car, TurretMotor

from buttons import shoot, lights

HOST = "0.0.0.0"
PORT_HUD = 2222
PORT_GRAPH = 2223
PORT_BUTTONS = 2224
PORT_JOYSTICK = 2225



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
            conn.sendall(b'ACK')

            if new_state == "idle":
                GPIO.output(Yellow, GPIO.LOW)
                GPIO.output(White, GPIO.HIGH)
                GPIO.output(Green, GPIO.LOW)
                turret.move(0.7, 0.7)

            elif new_state == "Operative":
                GPIO.output(Yellow, GPIO.LOW)
                GPIO.output(White, GPIO.LOW)
                GPIO.output(Green, GPIO.HIGH)

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
            GPIO.output(PIN, GPIO.LOW if value == 1 else GPIO.HIGH)
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
        Canisters = [True, True, True]
        conn.sendall(str(Canisters).encode())
        CurrentCanister = 0
        print(f"[BUTTONS] Connected to {addr}")

        while True:
            data = safe_recv(conn, 2048)
            if not data:
                break

            msg = data.decode().strip()
            buttons = msg.split(",")

            a = int(buttons[0])
            b = int(buttons[1])
            x = int(buttons[2])
            y = int(buttons[3])
            shoulder_l = int(buttons[4])
            shoulder_r = int(buttons[5])

            if get_state() == "Operative":
                if shoulder_l == 1:
                    Canisters = shooting.reload(Canisters, CurrentCanister)
                    conn.sendall(str(Canisters).encode())
                if shoulder_r == 1:
                    Canisters = shooting.shot(Canisters, CurrentCanister)
                    conn.sendall(str(Canisters).encode())
                if a == 1:
                    light.front(a)
                if b == 1:
                    if CurrentCanister != 2:
                        CurrentCanister +=1
                        
                    else:
                        CurrentCanister = 0
                if x == 1:
                    if CurrentCanister != 0:
                        CurrentCanister -= 1
                    else:
                        CurrentCanister = 2
                print("Selected Canister: ", CurrentCanister + 1)
                sleep(0.1)

        conn.close()


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
                car_speed = int(values[1]) / -32768
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




GPIO.setmode(GPIO.BCM)
PIN = 17
Yellow = 35
White = 37
Green = 40
wheels = Car(
    EnaA=11, In1A=13, In2A=15,
    EnaB=29, In1B=31, In2B=33,
    steeringPin=5,
    turretHorPin=8,
    turretVertPin=10
)



turret = wheels.turret  

shooting = shoot(19, 21, 23)
light = lights(24, 26, 28)

GPIO.setup(PIN, GPIO.OUT)
GPIO.setup(Yellow, GPIO.OUT)
GPIO.setup(White, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)

if state == "Connect":
    GPIO.output(Yellow, GPIO.HIGH)
    GPIO.output(White, GPIO.LOW)
    GPIO.output(Green, GPIO.LOW)




threading.Thread(target=hud_server, daemon=True).start()
threading.Thread(target=graph_server, daemon=True).start()
threading.Thread(target=buttons_server, daemon=True).start()
threading.Thread(target=joystick_server, daemon=True).start()

while True:
    sleep(0.1)
