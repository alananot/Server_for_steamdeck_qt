import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)


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
        self.pwmB.start(90)
    
    def setTurn(angle):
        duty_cycle = (angle/18) + 2.5
        pwm.ChangeDutyCycle(duty_cycle)
        sleep(0.01)
        
    def car_move(self, speed=0, turn=0, t=0):
        print(speed, turn)
        speed *= 100
        turn *= 180
        turning = setTurn(turn)
        
        leftWheel = max(min(speed - turn, 100), -100)
        rightWheel = max(min(speed + turn, 100), -100)


        self.pwmA.ChangeDutyCycle(abs(leftWheel))
        self.pwmB.ChangeDutyCycle(abs(rightWheel))


        GPIO.output(self.In1A, GPIO.LOW if leftWheel > 0 else GPIO.HIGH)
        GPIO.output(self.In2A, GPIO.HIGH if leftWheel > 0 else GPIO.LOW)

        GPIO.output(self.In1B, GPIO.LOW if rightWheel > 0 else GPIO.HIGH)
        GPIO.output(self.In2B, GPIO.HIGH if rightWheel > 0 else GPIO.LOW)

        sleep(t)

    def stop(self, t=0):
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)
        sleep(t)



class TurretMotor:
    def __init__(self, servoHorPin, servoVertPin):
        self.servoHorPin = servoHorPin
        self.servoVertPin = servoVertPin

        GPIO.setup(self.servoHorPin, GPIO.OUT)
        GPIO.setup(self.servoVertPin, GPIO.OUT)


        self.pwmHor = GPIO.PWM(self.servoHorPin, 50)
        self.pwmVert = GPIO.PWM(self.servoVertPin, 50)

        self.pwmHor.start(7.5)
        self.pwmVert.start(7.5)


    def _servo_speed_to_duty(self, speed):

        pulse = 7.5 + (speed * 2.5)
        return pulse

    def move(self, horizontal=0.0, vertical=0.0, t=0):

        horizontal = max(min(horizontal, 1.0), -1.0)
        vertical = max(min(vertical, 1.0), -1.0)


        horDuty = self._servo_speed_to_duty(horizontal)
        vertDuty = self._servo_speed_to_duty(vertical)
        print(horDuty, vertDuty)
        

        self.pwmHor.ChangeDutyCycle(horDuty)
        self.pwmVert.ChangeDutyCycle(vertDuty)
        #print(self.pwmVert, self.pwmHor)
        sleep(t)

    def stop(self, t=0):
        self.pwmHor.ChangeDutyCycle(7.5) 
        self.pwmVert.ChangeDutyCycle(7.5)
        sleep(t)
