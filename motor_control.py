import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

class SteeringServo:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(7.5)
        #print(f"[SteeringServo] Init on pin {self.pin}, start duty 7.5")

    def set_angle(self, angle):
        #print(f"[SteeringServo] Input angle: {angle}")
        angle = max(min(angle, 45), -45)
        #print(f"[SteeringServo] Clamped angle: {angle}")

        duty = 7.5 + (angle / 18)
        #print(f"[SteeringServo] Duty cycle: {duty}")

        self.pwm.ChangeDutyCycle(duty)
        sleep(0.02)

    def center(self):
        #print("[SteeringServo] Centering (7.5 duty)")
        self.pwm.ChangeDutyCycle(7.5)


class CarMotor:
    def __init__(self, EnaA, In1A, In2A, EnaB, In1B, In2B):
        self.EnaA = EnaA
        self.In1A = In1A
        self.In2A = In2A
        self.EnaB = EnaB
        self.In1B = In1B
        self.In2B = In2B

        GPIO.setup(self.EnaA, GPIO.OUT)
        GPIO.setup(self.In1A, GPIO.OUT)
        GPIO.setup(self.In2A, GPIO.OUT)
        GPIO.setup(self.EnaB, GPIO.OUT)
        GPIO.setup(self.In1B, GPIO.OUT)
        GPIO.setup(self.In2B, GPIO.OUT)

        self.pwmA = GPIO.PWM(self.EnaA, 100)
        self.pwmB = GPIO.PWM(self.EnaB, 100)

        self.pwmA.start(0)
        self.pwmB.start(0)

        #print("[CarMotor] Motor driver initialized")

    def move(self, speed=0.0, t=0.1):
        #print(f"[CarMotor] Input speed: {speed}")

        speed = max(min(speed, 1.0), -1.0)
        #print(f"[CarMotor] Clamped speed: {speed}")

        duty = abs(speed) * 100
        #print(f"[CarMotor] Duty cycle: {duty}")

        direction = "forward" if speed > 0 else "reverse"
        #print(f"[CarMotor] Direction: {direction}")

        self.pwmA.ChangeDutyCycle(duty)
        GPIO.output(self.In1A, GPIO.LOW if speed > 0 else GPIO.HIGH)
        GPIO.output(self.In2A, GPIO.HIGH if speed > 0 else GPIO.LOW)

        self.pwmB.ChangeDutyCycle(duty)
        GPIO.output(self.In1B, GPIO.LOW if speed > 0 else GPIO.HIGH)
        GPIO.output(self.In2B, GPIO.HIGH if speed > 0 else GPIO.LOW)

        sleep(t)

    def stop(self):
       # print("[CarMotor] STOP (duty=0)")
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)


class TurretMotor:
    def __init__(self, servoHorPin, servoVertPin):
        self.servoHorPin = servoHorPin
        self.servoVertPin = servoVertPin

       # print(f"[INIT] Horisontell pin: {self.servoHorPin}, Vertikal pin: {self.servoVertPin}")

        GPIO.setup(self.servoHorPin, GPIO.OUT)
        GPIO.setup(self.servoVertPin, GPIO.OUT)

        self.pwmHor = GPIO.PWM(self.servoHorPin, 50)
        self.pwmVert = GPIO.PWM(self.servoVertPin, 50)

        self.pwmHor.start(7.5)
        self.pwmVert.start(7.5)

        #print("[INIT] PWM startad på båda servon med duty 7.5")

    def _duty_270(self, angle):
        angle = max(min(angle, 270), 0)
        duty = 2.5 + angle/27
        #print(f"[DUTY_270] Input: {angle}, Duty: {duty:.2f}")
        
        return duty

    def _duty_45(self, angle):
        angle = max(min(angle, 45), 0)
        duty = 2.5 + (angle / 18)
        print(f"[DUTY_45] Input: {angle}, Duty: {duty:.2f}")
        return duty

    def move(self, horizontal=135.0, vertical=45.0, t=0):
        #print(f"[MOVE] Horisontell: {horizontal}, Vertikal: {vertical}, Tid: {t}")

        horDuty = self._duty_270(horizontal)
        vertDuty = self._duty_45(vertical)

       # print(f"[MOVE] HorDuty: {horDuty:.2f}, VertDuty: {vertDuty:.2f}")

        self.pwmHor.ChangeDutyCycle(horDuty)
        self.pwmVert.ChangeDutyCycle(vertDuty)

        sleep(t)

    def stop(self):
        #print("[STOP] Återställer horisontell servo till 7.5 duty")
        self.pwmHor.ChangeDutyCycle(7.5)

class Car:
    def __init__(self,
                 EnaA, In1A, In2A,
                 EnaB, In1B, In2B,
                 steeringPin,
                 turretHorPin,
                 turretVertPin):

        #print("[Car] Initializing subsystems...")
        self.drive = CarMotor(EnaA, In1A, In2A, EnaB, In1B, In2B)
        self.steering = SteeringServo(steeringPin)
        self.turret = TurretMotor(turretHorPin, turretVertPin)
        #print("[Car] Initialization complete")

    def move(self, speed, steering_angle, t=0):
        #print(f"[Car] MOVE speed:{speed} steering:{steering_angle}")
        self.steering.set_angle(steering_angle)
        self.drive.move(speed, t)

    def stop(self):
        #print("[Car] STOP all systems")
        self.drive.stop()
        self.steering.center()
        self.turret.stop()


if __name__ == "__main__":
    car = Car(
        EnaA=17, In1A=27, In2A=22,
        EnaB=23, In1B=24, In2B=25,
        steeringPin=5,
        turretHorPin=6,
        turretVertPin=13
    )

    try:
        car.move(speed=0.5, steering_angle=20, t=1)
        car.turret.move(horizontal=0, vertical=0, t=1)
        car.stop()

    except KeyboardInterrupt:
        car.stop()
        GPIO.cleanup()
