import serial
a = 1
b = 678
ser = serial.Serial('/dev/serial0', 115200)

print("Waiting for data from ESP...")

while True:
    ser.write(f"{a},{b}\n".encode())
    message = ser.readline().decode().strip()
    print(message)