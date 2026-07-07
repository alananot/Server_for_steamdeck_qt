#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// -------------------- WiFi Setup --------------------
const char* ssid = "ESP32S3_AP";
const char* password = "12345678";

WiFiServer hudServer(2222);
WiFiServer graphServer(2223);
WiFiServer buttonsServer(2224);
WiFiServer joystickServer(2225);

WiFiClient hudClient;
WiFiClient graphClient;
WiFiClient buttonsClient;
WiFiClient joystickClient;

unsigned long lastGraphTime = 0; 
bool joystickSafetyTriggered = false;

// -------------------- PCA9685 Servo Driver --------------------
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);
#define SERVO_MIN_CAR 220
#define SERVO_MID 288
#define SERVO_MAX_CAR 353
#define SERVO_DELAY 1000
#define NUM_SERVOS 1
#define TURRET_HOR 1
#define TURRET_VERT 2
#define TURRET_HOR_MAX 450
#define TURRET_HOR_MIN 100
int TURRET_HOR_POS = 288;
int STEERING_CHANNEL = 0;

const int PWM_in = 13;
const int PWM_inh = 14;
const int Rear = 37;
// -------------------- GPIO Pins --------------------
const int PIN = 1;      
const int Yellow = 2;   
const int White  = 42;  
const int Green  = 21;  

#define MOTOR_ENA 4
#define MOTOR_IN1 5
#define MOTOR_IN2 6
#define MOTOR_ENB 7
#define MOTOR_IN3 15
#define MOTOR_IN4 16

// --- NYA PINNAR FÖR SHOOT OCH LIGHTS (Ändra dessa till dina faktiska pinnar!) ---
#define SHOOT_IN1 10
#define SHOOT_IN2 11
#define SHOOT_IN3 12

#define LIGHT_ENA 38
#define LIGHT_IN1 39 // Baklyktor
#define LIGHT_IN2 40 // Framlyktor
// -------------------------------------------------------------------------------

String state = "Operative"; 
void set_state(String newState) { state = newState; }
String get_state() { return state; }

bool Canisters[3] = {true, true, true};
int CurrentCanister = 0;

// ==========================================================
//            HARDWARE CLASSES
// ==========================================================

// --- INTEGRERAD: Shoot ---
class Shoot {
private:
    int pin1, pin2, pin3;
public:
    Shoot(int in1, int in2, int in3) {
        pin1 = in1; pin2 = in2; pin3 = in3;
    }
    void begin() {
        pinMode(pin1, OUTPUT);
        pinMode(pin2, OUTPUT);
        pinMode(pin3, OUTPUT);
    }
    void reload(bool cans[], int currentCanister) {
        if (cans[currentCanister] == false) {
            if (currentCanister == 0) {
                digitalWrite(pin1, LOW);
                cans[0] = true;
                Serial.println("First canister reloaded");
            } else if (currentCanister == 1) {
                digitalWrite(pin2, LOW);
                cans[1] = true;
                Serial.println("Second canister reloaded");
            } else if (currentCanister == 2) {
                digitalWrite(pin3, LOW);
                cans[2] = true;
                Serial.println("Third canister reloaded");
            }
        } else {
            Serial.print("Canister "); Serial.print(currentCanister + 1); Serial.println(" is already loaded");
            for (int i = 0; i < 3; i++) {
                if (cans[i] == false) return;
            }
            Serial.println("All Canisters are loaded");
        }
    }
    void shot(bool cans[], int currentCanister) {
        if (cans[currentCanister] == true) {
            if (currentCanister == 0) {
                digitalWrite(pin1, HIGH);
                cans[0] = false;
                Serial.println("First canister launched");
            } else if (currentCanister == 1) {
                digitalWrite(pin2, HIGH);
                cans[1] = false;
                Serial.println("Second canister launched");
            } else if (currentCanister == 2) {
                digitalWrite(pin3, HIGH);
                cans[2] = false;
                Serial.println("Third canister launched");
            }
        } else {
            for (int i = 0; i < 3; i++) {
                if (cans[i] == true) {
                    Serial.print("Canister "); Serial.print(currentCanister + 1); Serial.println(" is empty");
                    return;
                }
            }
            Serial.println("All Canisters are empty");
        }
    }
};

// --- INTEGRERAD: Lights ---
class Lights {
private:
    int enaPin, in1Pin, in2Pin;
    int lightStrength;
public:
    Lights(int ena, int in1, int in2) {
        enaPin = ena; in1Pin = in1; in2Pin = in2;
        lightStrength = 0;
    }
    void begin() {
        pinMode(enaPin, OUTPUT);
        pinMode(in1Pin, OUTPUT);
        pinMode(in2Pin, OUTPUT);
        analogWrite(enaPin, 0); 
    }
    void rear() {
        digitalWrite(in1Pin, HIGH);
    }
    void front(int a = 0) {
        if (a == 1 && lightStrength != 100) {
            digitalWrite(in2Pin, HIGH);
            lightStrength = 100;
            analogWrite(enaPin, 255); // Max PWM för ESP32 analogWrite
           // Serial.println("Beam lights on");
        } else if (a == 0) {
            lightStrength = 0;
            digitalWrite(in2Pin, LOW);
            analogWrite(enaPin, 0);
            //Serial.println("Beam lights off");
        }
    }
};

class SteeringServo {
    private: 
    unsigned long prev_blink = 0;

    const int interval = 250;
    int blinkState = HIGH;
public:
    int channel;
    SteeringServo(int pwmChannel) {
        channel = pwmChannel;
        pwm.setPWM(0, 0, SERVO_MAX_CAR);
    }
    void set_angle(float angle) {
        unsigned long blinkStart = millis();
        float tot_angle = angle * -65;
        tot_angle += SERVO_MID;
        if (tot_angle > SERVO_MID &&  blinkStart - prev_blink >= interval){
            prev_blink = blinkStart;

            if(blinkState == LOW){
                blinkState = HIGH;
            }
            else
            {
                blinkState = LOW;
            }

            digitalWrite(Rear, blinkState);



        }
        //Serial.print(blinkStart);
        if (tot_angle > SERVO_MAX_CAR) tot_angle = SERVO_MAX_CAR;
        if (tot_angle < SERVO_MIN_CAR) tot_angle = SERVO_MIN_CAR;
        pwm.setPWM(0, 0, tot_angle);
    }
    void center() { pwm.setPWM(0, 0, SERVO_MID); }
};

class CarMotor {
public:
    int EnaA, In1A, In2A, EnaB, In1B, In2B;
    CarMotor(int enaA, int in1A, int in2A, int enaB, int in1B, int in2B) {
        EnaA = enaA; In1A = in1A; In2A = in2A;
        EnaB = enaB; In1B = in1B; In2B = in2B;
        pinMode(EnaA, OUTPUT); pinMode(In1A, OUTPUT); pinMode(In2A, OUTPUT);
        pinMode(EnaB, OUTPUT); pinMode(In1B, OUTPUT); pinMode(In2B, OUTPUT);
    }
    void move(float speed, float angle) {
        speed = constrain(speed, -1.0f, 1.0f);
        speed *= 20;
        //Serial.println(speed);
        if (speed < 0)
        {
             front_light(true);
        }
        else if(speed >= 2000 ){
            front_light(false);
        }

        digitalWrite(PWM_inh, HIGH);
        analogWrite(PWM_in, abs(speed));
    }
    void stop() {
        digitalWrite(PWM_inh, LOW);
        analogWrite(PWM_in, 0);
        front_light(true);
        //Serial.println("Stopping");
    }
};

class TurretMotor {
public:
    int horChannel, vertChannel;
    TurretMotor(int hor, int vert) {
        horChannel = hor; vertChannel = vert;
        pwm.setPWM(TURRET_HOR, 0, SERVO_MID);
        pwm.setPWM(TURRET_VERT, 0, 0);
    }
    int duty270(float angle) {
        //Serial.print("Torn vinkel: ");
        //Serial.println(angle);
        if(angle < 0){
            angle *= 10;
        }
        if(angle > 0){
            angle *= 10;
        }
        if(TURRET_HOR_POS <= TURRET_HOR_MAX && TURRET_HOR_POS >= TURRET_HOR_MIN)
        {
            TURRET_HOR_POS += angle;
        }
        else if(TURRET_HOR_POS >= TURRET_HOR_MAX)
        {
            TURRET_HOR_POS = TURRET_HOR_MAX;
        }
        else
        {
            TURRET_HOR_POS  = TURRET_HOR_MIN;
        }
           //delay(15);
        return TURRET_HOR_POS;
    }
    int duty45(float angle) {
        angle = constrain(angle, 0, 45);
        float duty = 2.5 + angle / 18.0;
        return map(duty * 10, 0, 250, SERVO_MIN_CAR, SERVO_MAX_CAR);
    }
    void move(float horizontal, float vertical) {
        pwm.setPWM(horChannel, 0, duty270(horizontal));
        pwm.setPWM(vertChannel, 0, duty45(vertical));
    }
    void stop() {
        Serial.println("Stoopar torn");
        TURRET_HOR_POS = SERVO_MID;
        pwm.setPWM(horChannel, 0, SERVO_MID);
        pwm.setPWM(vertChannel, 0, SERVO_MID);
    }
};

class Car {
public:
    CarMotor drive; SteeringServo steering; TurretMotor turret;
    Car(int EnaA, int In1A, int In2A, int EnaB, int In1B, int In2B, int steeringChannel, int turretHorChannel, int turretVertChannel)
        : drive(EnaA, In1A, In2A, EnaB, In1B, In2B), steering(steeringChannel), turret(turretHorChannel, turretVertChannel) {}
    void move(float speed, float steering_angle) {
        steering.set_angle(steering_angle);
        drive.move(speed, steering_angle);
    }
    void stop() { drive.stop(); steering.center(); turret.stop(); }
};

// ==========================================================
//            GLOBAL INSTANCES
// ==========================================================
Car* myRobot = nullptr;
Shoot myShooter(SHOOT_IN1, SHOOT_IN2, SHOOT_IN3);
Lights myLights(LIGHT_ENA, LIGHT_IN1, LIGHT_IN2);

// ==========================================================
//            HELPER FUNCTIONS
// ==========================================================
void wheels_move(float speed, float turn) { if (myRobot) myRobot->move(speed, turn * 45.0f); }
void wheels_stop() { if (myRobot) { myRobot->drive.stop(); myRobot->steering.center(); } }
void turret_move(float h, float v) { if (myRobot) myRobot->turret.move(h, v); }
void turret_stop() { if (myRobot) myRobot->turret.stop(); }

// Uppdaterade metoder som använder de nya klasserna
void reload_canister() { 
    myShooter.reload(Canisters, CurrentCanister); 
}
void shoot_canister() { 
    myShooter.shot(Canisters, CurrentCanister); 
}
void front_light(bool on) { 
    digitalWrite(Rear, on ? HIGH : LOW); // Din befintliga vita status-LED (om du vill ha kvar den)
    myLights.front(on ? 1 : 0);           // Styr riktig belysning via Lights-klassen
}

// ==========================================================
//            FIXED ASYNC SERVER HANDLERS WITH TIMEOUTS
// ==========================================================

void handleHUD() {
    if (!hudClient.connected()) {
        hudClient.stop(); 
        hudClient = hudServer.accept(); 
        if (hudClient) {
            hudClient.setTimeout(1);
        }
    }

    if (hudClient && hudClient.available()) {
        String data = hudClient.readStringUntil('\n');
        data.trim();

        if (data.length() > 0) {
            set_state(data);
            hudClient.print("ACK\n");

            if (data == "idle") {
                digitalWrite(Yellow, LOW); digitalWrite(White, HIGH); digitalWrite(Green, LOW);
                turret_move(135, 0);
            }
            else if (data == "Operative") {
                digitalWrite(Yellow, LOW); digitalWrite(White, LOW); digitalWrite(Green, HIGH);
            }
        }
    }
}

void handleGraph() {
    if (!graphClient.connected()) {
        graphClient.stop();
        graphClient = graphServer.accept();
        if (graphClient) {
            graphClient.setTimeout(1);
        }
    }

    if (graphClient && graphClient.connected()) {
        if (millis() - lastGraphTime >= 50) {
            int Raw3v3 = analogRead(17); 
            float voltage3v3 = (Raw3v3 / 4095.0) * 3.3;
            float sensorV = voltage3v3 * (37.0 / 22.0);
            float current = (sensorV - 2.5) / 0.2;

            lastGraphTime = millis();
            int value = digitalRead(PIN);
            digitalWrite(17, value == HIGH ? LOW : HIGH);
            graphClient.println(current); 
        }
    }
}

void handleButtons() {
    if (!buttonsClient.connected()) {
        buttonsClient.stop();
        buttonsClient = buttonsServer.accept();
        if (buttonsClient) {
            buttonsClient.setTimeout(1); 
            buttonsClient.print("[true,true,true]\n");
        }
    }

    if (buttonsClient && buttonsClient.available()) {
        String msg = buttonsClient.readStringUntil('\n');
        msg.trim();

        if (msg.length() > 0) {
            int a, b, x, y, shoulder_l, shoulder_r;
            if (sscanf(msg.c_str(), "%d,%d,%d,%d,%d,%d", &a, &b, &x, &y, &shoulder_l, &shoulder_r) == 6) {
                if (get_state() == "Operative") {
                    if (shoulder_l == 1) {
                        reload_canister();
                        buttonsClient.print(String(Canisters[0]) + "," + String(Canisters[1]) + "," + String(Canisters[2]) + "\n");
                    }
                    if (shoulder_r == 1) {
                        shoot_canister();
                        buttonsClient.print(String(Canisters[0]) + "," + String(Canisters[1]) + "," + String(Canisters[2]) + "\n");
                    }
                    
                    // Toggle light based on 'a' button. (Using simplistic turn-on/off as requested)
                    if (a == 1) front_light(true); 
                    else front_light(false); // Added toggle off support

                    if (b == 1) CurrentCanister = (CurrentCanister + 1) % 3;
                    if (x == 1) CurrentCanister = (CurrentCanister + 2) % 3;

                    Serial.print("Selected Canister: ");
                    Serial.println(CurrentCanister + 1);
                }
            }
        }
    }
}

void handleJoystick() {
    if (!joystickClient.connected()) {
        joystickClient.stop();
        joystickClient = joystickServer.accept();
        if (joystickClient) {
            joystickClient.setTimeout(1);
            joystickSafetyTriggered = false; 
        }
    }

    if (joystickClient && joystickClient.connected()) {
        if (joystickClient.available()) {
            String msg = joystickClient.readStringUntil('\n');
            msg.trim();

            if (msg.length() > 0) {
                int v0, v1, v2, v3;
                if (sscanf(msg.c_str(), "%d,%d,%d,%d", &v0, &v1, &v2, &v3) == 4) {
                    float car_turn = v0 / -32768.0f;
                    float car_speed = v1 / -32768.0f;
                    float turret_h = (v2 / -32768.0f);
                    float turret_v = (v3 / -32768.0f);
                    Serial.print(turret_h);
                    Serial.print(" ");
                    Serial.print(turret_v);
                    Serial.println();
                    if (get_state() == "Operative") {
                        if (abs(car_speed) > 0.05f || abs(car_turn) > 0.05f) {
                            myRobot->move(car_speed, car_turn);
                        } else {
                            //myRobot->stop();
                        }

                        
                            turret_move(turret_h, turret_v);
                        
                        //Serial.println(TURRET_HOR_POS);
                    }
                }
            }
            /*else {
                myRobot->stop();
                turret_stop();
            }*/
        }
    } else {
        if (!joystickSafetyTriggered) {
            wheels_stop();
            turret_stop();
            joystickSafetyTriggered = true;
        }
    }
}

// -------------------- Setup --------------------
void setup() {
    Serial.begin(115200);
    
    // Initiera servos
    pwm.begin();
    pwm.setPWMFreq(50);
    pwm.setPWM(0, 0, 300);
    
    // Status LEDs och system-pins
    pinMode(PWM_in, OUTPUT); pinMode(Yellow, OUTPUT); pinMode(White, OUTPUT); pinMode(Green, OUTPUT);
    digitalWrite(Yellow, HIGH); digitalWrite(White, LOW); digitalWrite(Green, LOW);
    pinMode(PWM_in,OUTPUT);
    pinMode(PWM_inh,OUTPUT);
    digitalWrite(PWM_inh, HIGH);
    pinMode(Rear, OUTPUT);
    pwm.setPWM(TURRET_HOR, 0, SERVO_MID);
    // Initiera nya klasser
    myShooter.begin();
    myLights.begin();

    // WiFi Setup
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password);

    // Servrar
    hudServer.begin();
    graphServer.begin();
    buttonsServer.begin();
    joystickServer.begin();

    myRobot = new Car(MOTOR_ENA, MOTOR_IN1, MOTOR_IN2, MOTOR_ENB, MOTOR_IN3, MOTOR_IN4, STEERING_CHANNEL, TURRET_HOR, TURRET_VERT);

    Serial.println("ESP32 System Online");
}
// -------------------- Main Loop --------------------
void loop() {
    handleHUD();
    handleGraph();
    handleButtons();
    handleJoystick();
    //Serial.println(TURRET_HOR_POS);
    static unsigned long lastSerialPrint = 0;
    if (millis() - lastSerialPrint >= 500) {
        lastSerialPrint = millis();
    }
}
