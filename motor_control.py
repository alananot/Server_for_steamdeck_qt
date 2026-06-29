
import RPi.GPIO as GPIO
import lgpio
from time import sleep
GPIO.setmode(GPIO.BCM)

class CarMotor():
    def __init__(self,EnaA, In1A, In2A, EnaB,In1B,In2B):
        self.EnaA = EnaA
        self.In1A = In1A
        self.In2A = In2A
        self.EnaB = EnaB
        self.In1B = In1B
        self.In2B = In2B
        GPIO.setup(self.EnaA,GPIO.OUT)
        GPIO.setup(self.In1A, GPIO.OUT)
        GPIO.setup(self.In2A, GPIO.OUT)
        GPIO.setup(self.EnaB,GPIO.OUT)
        GPIO.setup(self.In1B, GPIO.OUT)
        GPIO.setup(self.In2B, GPIO.OUT)
        self.pwmA = GPIO.PWM(self.EnaA, 100);
        self.pwmA.start(0);
        self.pwmB = GPIO.PWM(self.EnaB, 100);
        self.pwmB.start(0);
        
        
    def car_move(self,speed = 0,turn = 0, t= 0):
        speed *= 100
        turn *= 100
        
        leftWheel = speed - turn
        rightWheel = speed + turn
        
        if(leftWheel > 100):
            leftWheel = 100
        elif(leftWheel < -100):
            leftWheel = -100
        
        if(rightWheel > 100):
            rightWheel = 100
        elif(rightWheel < -100):
            rightWheel = -100
        
        
        
        self.pwmA.ChangeDutyCycle(abs(leftWheel))
        self.pwmB.ChangeDutyCycle(abs(rightWheel))
        
        if(leftWheel> 0):
            GPIO.output(self.In1A,GPIO.LOW)
            GPIO.output(self.In2A,GPIO.HIGH)
        else:
            GPIO.output(self.In1A,GPIO.HIGH)
            GPIO.output(self.In2A,GPIO.LOW)
        
        if(rightWheel > 0):
            GPIO.output(self.In1B,GPIO.LOW)
            GPIO.output(self.In2B,GPIO.HIGH)
        else:
            GPIO.output(self.In1B,GPIO.HIGH)
            GPIO.output(self.In2B,GPIO.LOW)
        
        
        sleep(t)
    def stop(self,t = 0):
        self.pwmA.ChangeDutyCycle(0);
        self.pwmB.ChangeDutyCycle(0);
        sleep(t)
        
class TurretMotor():
    def __init__(self,EnaA, In1A, In2A, EnaB,In1B,In2B):
        self.EnaA = EnaA
        self.In1A = In1A
        self.In2A = In2A
        self.EnaB = EnaB
        self.In1B = In1B
        self.In2B = In2B
        GPIO.setup(self.EnaA,GPIO.OUT)
        GPIO.setup(self.In1A, GPIO.OUT)
        GPIO.setup(self.In2A, GPIO.OUT)
        GPIO.setup(self.EnaB,GPIO.OUT)
        GPIO.setup(self.In1B, GPIO.OUT)
        GPIO.setup(self.In2B, GPIO.OUT)
        self.pwmA = GPIO.PWM(self.EnaA, 100);
        self.pwmA.start(0);
        self.pwmB = GPIO.PWM(self.EnaB, 100);
        self.pwmB.start(0);
        
        
    def turret_move(self, horizontal= 0, vertical= 0, t= 0):
        horizontal *= 100
        vertical *= 100
        
        
        
        
        if(horizontal > 100):
            horizontal = 100
        elif(horizontal < -100):
            horizontal = -100
        
        if(vertical > 100):
            vertical = 100
        elif(vertical < -100):
            vertical = -100
        
        
        
        self.pwmA.ChangeDutyCycle(abs(horizontal))
        self.pwmB.ChangeDutyCycle(abs(vertical))
        
        if(horizontal> 0):
            GPIO.output(self.In1A,GPIO.LOW)
            GPIO.output(self.In2A,GPIO.HIGH)
        else:
            GPIO.output(self.In1A,GPIO.HIGH)
            GPIO.output(self.In2A,GPIO.LOW)
        
        if(vertical > 0):
            GPIO.output(self.In1B,GPIO.LOW)
            GPIO.output(self.In2B,GPIO.HIGH)
        else:
            GPIO.output(self.In1B,GPIO.HIGH)
            GPIO.output(self.In2B,GPIO.LOW)
        
        
        sleep(t)
    def stop(self,t = 0):
        self.pwmA.ChangeDutyCycle(0);
        self.pwmB.ChangeDutyCycle(0);
        sleep(t)