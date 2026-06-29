
import RPi.GPIO as GPIO
import lgpio
from time import sleep
GPIO.setmode(GPIO.BCM)
Canister1 = True
Canister2 = True
Canister3 = True


class shoot():

    
    def __init__(self, Ena, In1,In2,In3):
        self.Ena = Ena
        self.In1 = In1
        self.In2 = In2
        self.In3 = In3
        GPIO.setup(self.Ena,GPIO.OUT)
        GPIO.setup(self.In1, GPIO.OUT)
        GPIO.setup(self.In2, GPIO.OUT)
        GPIO.setup(self.In3, GPIO.OUT)
        self.pwmA = GPIO.PWM(self.Ena, 100);
        self.pwmA.start(0);
        
    
    def shot(self):
        if(Canister1):
            GPIO.output(self.In1, GPIO.HIGH)
        elif(Canister1 == false):
            GPIO.output(self.In2, GPIO.HIGH)
        else:
            GPIO.output(self.In3, GPIO.HIGH)


class lights():
    def __init__(self,Ena, In1,In2):
        self.Ena = Ena
        self.In1 = In1
        self.In2 = In2
        GPIO.setup(self.Ena,GPIO.OUT)
        GPIO.setup(self.In1, GPIO.OUT)
        GPIO.setup(self.In2, GPIO.OUT)
        self.pwmA = GPIO.PWM(self.Ena, 100);
        self.pwmA.start(60);
        
    def rear(self):
        GPIO.output(self.In1, GPIO.HIGH)
    
    def front(self):
        GPIO.output(self.In2, GPIO.HIGH)
    