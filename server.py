import socket
import lgpio
import threading
HOST = "0.0.0.0"
PORT_HUD = 2222
PORT_GRAPH = 2223
PORT_BUTTONS = 2224
PORT_JOYSTICK = 2225

PIN = 7

state = "Connect"

chip = lgpio.gpiochip_open(0)

lgpio.gpio_claim_input(chip, PIN)


def hud_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT_HUD))
    server.listen(1)
    print(f"[HUD listening on {HOST}:{PORT_HUD}]")
    
    while True:
        conn,addr = server.accept()
        print(f"[HUD] Connected to {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            state = data.decode()
            
            print("Current:", state)
            
            conn.sendall(b'ACK')
        conn.close()
    

    
    
def graph_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT_GRAPH))
    server.listen(1)
    print(f"[GRAPH] listening on {HOST}:{PORT_GRAPH}]")
    while True:
        conn,addr = server.accept()
        print(f"[GRAPH] Connected to {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            value = lgpio.gpio_read(chip, PIN)
            conn.sendall(str(value).encode())
        conn.close()
    

   
   
def buttons_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT_BUTTONS))
    server.listen(1)
    print(f"[BUTTONS] listening on {HOST}:{PORT_BUTTONS}]")
    while True:
        conn,addr = server.accept()
        print(f"[BUTTONS] Connected to {addr}")
        data = []
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            buttons = msg.split(",")
            a = buttons[0]
            b = buttons[1]
            x = buttons[2]
            y = buttons[3]
            shoulder_l = buttons[4]
            shoulder_r = buttons[5]
            if states == "Operative"
            print(f"A: {a}\n, B = {b}\n, X = {x}\n, y = {y}\n, Shoulder left trigger: {shoulder_l}\n, Shoulder right trigger: {shoulder_r}")
        conn.close()
    
    
def joystick_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT_JOYSTICK))
    server.listen(1)
    print(f"[Joystick] listening on {HOST}:{PORT_JOYSTICK}]")
    
    while True:
        conn,addr = server.accept()
        print(f"[Joystick] Connected to {addr}")
        
        data = []
        while True:
            data = conn.recv(2048)
            if not data:
                break
            msg = data.decode().strip()
            
            values = msg.split(",")
            car_turn = int(values[0])
            car_speed = int(values[1])
            turret_horizontal = int(values[2])
            turret_vertical = int(values[3])
            right_trig = int(values[4])
            left_trig = int(values[5])
            print(f"Car turning: {car_turn}, Car speed: {car_speed}, Turret horizontal: {turret_horizontal}, Turret vertical: {turret_vertical}, Firing: {right_trig}, Zooming: {left_trig}")
            if states == "Operative":
                
        conn.close()
    


threading.Thread(target=hud_server, daemon=True).start()
threading.Thread(target=graph_server, daemon=True).start()
threading.Thread(target=buttons_server, daemon=True).start()
threading.Thread(target=joystick_server, daemon=True).start()

while True:
    pass
