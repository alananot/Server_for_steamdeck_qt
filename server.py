import socket
import threading
import RPi.GPIO as GPIO
from motor_control import CarMotor, TurretMotor
from time import sleep
from buttons import shoot, lights
HOST = "0.0.0.0"
PORT_HUD = 2222
PORT_GRAPH = 2223
PORT_BUTTONS = 2224
PORT_JOYSTICK = 2225



PIN = 17
Yellow = 35
White = 37
Green = 40


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
                GPIO.output(Yellow, GPIO.LOW)
                GPIO.output(White, GPIO.HIGH)
                GPIO.output(Green, GPIO.LOW)
                turret.move(0.7,0.7)
            elif(new_state == "Operative"):
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
        Canisters = [True,True,True]

        #conn.settimeout(2)
        print(f"[BUTTONS] Connected to {addr}")

        while True:
            data = safe_recv(conn, 2048)
            #print(data)
            if not data:
                break
            
            msg = data.decode().strip()
            #print(msg)
            
            buttons = msg.split(",")
            a = int(buttons[0])
            b = int(buttons[1])
            x = int(buttons[2])
            y = int(buttons[3])
            shoulder_l = int(buttons[4])
            shoulder_r = int(buttons[5])
           # print(get_state())
            # print(f"A: {a}\n, B = {b}\n, X = {x}\n, y = {y}\n, Shoulder left trigger: {shoulder_l}\n, Shoulder right trigger: {shoulder_r}")
            if get_state() == "Operative":
                if(shoulder_r  == 1):
                    Canisters = shooting.shot(Canisters)
                    
                    #Canisters = [False,False,False]
                    #Canisters[0] = Canister1
                    #Canisters[1] = Canister2
                    #Canisters[2] = Canister3
                    #print("1: ",Canister1, "2: ",Canister2, "3: ",Canister3)
                    print(Canisters)
                    conn.sendall(str(Canisters).encode())
                if(a == 1):
                    light.front(a)

        conn.close()


def joystick_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT_JOYSTICK))
    server.listen(1)
    print(f"[Joystick listening on {HOST}:{PORT_JOYSTICK}]")

    while True:
        conn, addr = server.accept()
        #conn.settimeout(2)
        print(f"[Joystick] Connected to {addr}")

        while True:
            data = safe_recv(conn, 2048)
            if not data:
                break
            msg = "0,0,0,0"
            msg = data.decode().strip()
            values = msg.split(",")

            try:
                car_turn = int(values[0])
                car_speed = int(values[1])
                turret_horizontal = int(values[2])
                turret_vertical = int(values[3])
            except:
                car_turn = 0
                car_speed = 0
                turret_horizontal = 0
                turret_vertical = 0

            if get_state().lower() == "operative":
                if abs(car_speed) > 0 or abs(car_turn) > 0:
                    wheels.car_move(car_speed / 32768, car_turn / 32768)
                else:
                    wheels.stop()

                if abs(turret_horizontal) > 0 or abs(turret_vertical) > 0:
                    turret_horizontal /= 32768
                    turret_vertical /= 32768
                    turret.move(turret_horizontal,turret_vertical)
                else:
                    turret.stop()

        conn.close()


# Start servers
threading.Thread(target=hud_server, daemon=True).start()
threading.Thread(target=graph_server, daemon=True).start()
threading.Thread(target=buttons_server, daemon=True).start()
threading.Thread(target=joystick_server, daemon=True).start()
wheels = CarMotor(11, 13, 15, 29, 31, 33)
turret = TurretMotor(8, 10)
shooting = shoot(19,21,23)
light = lights(24,26,28)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
GPIO.setup(Yellow, GPIO.OUT)
GPIO.setup(White, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)
if(state == "Connect"):
    GPIO.output(Yellow, GPIO.HIGH)
    GPIO.output(White, GPIO.LOW)
    GPIO.output(Green, GPIO.LOW)


while True:
    sleep(0.1)
