
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
       
        
    
    def reload(self,Canisters, CurrentCanister):
        if(Canisters[CurrentCanister] == False):
            if(CurrentCanister == 0):
                GPIO.output(self.In1, GPIO.LOW)
                Canisters[CurrentCanister] = True
                print("First canister reloaded")

            elif(CurrentCanister == 1):
                GPIO.output(self.In2, GPIO.LOW)
                Canisters[CurrentCanister] = True
                print("Second canister reloaded")
            elif(CurrentCanister == 2):
                GPIO.output(self.In3, GPIO.LOW)
                Canisters[CurrentCanister] = True
                print("Third canister reloaded")
            return Canisters
        else:
            for i in Canisters:
                if(i == False):
                    print("Canister ", CurrentCanister +1, " is already loaded")
                    return Canisters
            print("All Canisters are loaded")
            return Canisters
        
    
    def shot(self,Canisters, CurrentCanister):
        

            
        
        if(Canisters[CurrentCanister] == True):
            if(CurrentCanister == 0):
                GPIO.output(self.In1, GPIO.HIGH)
                Canisters[CurrentCanister] = False
                print("First canister launched")

            elif(CurrentCanister == 1):
                GPIO.output(self.In2, GPIO.HIGH)
                Canisters[CurrentCanister] = False
                print("Second canister launched")
            elif(CurrentCanister == 2):
                GPIO.output(self.In3, GPIO.HIGH)
                Canisters[CurrentCanister] = False
                print("Third canister launched")
            return Canisters
        else:
            for i in Canisters:
                if(i == True):
                    print("Canister ",CurrentCanister +1, " is empty")
                    return Canisters
            print("All Canisters are empty")
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
            
        
    