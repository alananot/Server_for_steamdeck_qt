
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

class shoot():

    
    def __init__(self, In1,In2,In3):

        self.In1 = In1
        self.In2 = In2
        self.In3 = In3

       
        GPIO.setup(self.In1, GPIO.OUT)
        GPIO.setup(self.In2, GPIO.OUT)
        GPIO.setup(self.In3, GPIO.OUT)
       
        
    
    def shot(self,Canisters):
         
        
        if(Canisters[0] == True):
            GPIO.output(self.In1, GPIO.HIGH)
            Canisters[0] = False
            print("First canister launched")
        elif(Canisters[0] == False and Canisters[1] == True):
            GPIO.output(self.In2, GPIO.HIGH)
            Canisters[1] = False
            print("Second canister launched")
        elif(Canisters[0] == False and Canisters[1] == False and Canisters[2] == True):
            GPIO.output(self.In3, GPIO.HIGH)
            Canisters[2] = False
            print("Third canister launched")
        else:
            print("All canisters empty")
        return Canisters

class lights():
    def __init__(self,Ena, In1,In2):
        self.Ena = Ena
        self.In1 = In1
        self.In2 = In2
        self.lightStrength =0 
        GPIO.setup(self.Ena,GPIO.OUT)
        GPIO.setup(self.In1, GPIO.OUT)
        GPIO.setup(self.In2, GPIO.OUT)
        self.pwmA = GPIO.PWM(self.Ena, 100);
        self.pwmA.start(self.lightStrength);
        
    def rear(self):
        GPIO.output(self.In1, GPIO.HIGH)
    
    def front(self, a = 0):
        GPIO.output(self.In2, GPIO.HIGH)

        if(a == 1 and self.lightStrength != 100):
            self.lightStrength = 100
            self.pwmA.ChangeDutyCycle(self.lightStrength)
            print("Beam lights on")
        else:
            self.lightStrength = 0
            self.pwmA.ChangeDutyCycle(self.lightStrength)
            print("Beam lights off")
            
        
    