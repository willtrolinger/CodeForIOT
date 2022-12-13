import RPi.GPIO as GPIO
import PCF8591 as ADC
import time
import math
from gpiozero import AngularServo
from threading import Thread

class Sensors():
    # used to ativate and deactivate sensors
    sensors = {
        "IR Detector": True,
        "Active Buzzer": True,
        "Two Color LED": True,
        "Thermometer": True,
        "Motor": True
    }

    values = {
        "temp" : "",
        "color" : "",
        "angle" : ""
    }
    global p
    ObstaclePin = 29
    BuzzerPin = 11
    LedPins = (13, 15)
    ThermPin = 16
    MotorPin = 32

    currentTemp = 0

    Buzzer = None
    p_R = None
    p_G = None
    p = None

    colorToggle = False
    colors = [0xFF00, 0x00FF]
    
    angle = 0
    
    servo = ""
    #         Red     Green

    # constructor, takes the place of the GPIO setup function
    def __init__(self):
        ADC.setup(0x48)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.ObstaclePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.ThermPin, GPIO.IN)
        GPIO.setup(self.BuzzerPin, GPIO.OUT)
        GPIO.setup(self.LedPins, GPIO.OUT)
        GPIO.output(self.LedPins, GPIO.LOW)
        self.Buzzer = GPIO.PWM(self.BuzzerPin, 440)
        self.p_R = GPIO.PWM(self.LedPins[0], 2000)
        self.p_G = GPIO.PWM(self.LedPins[1], 2000)
        self.p_R.start(0)
        self.p_G.start(0)
        GPIO.setup(self.MotorPin, GPIO.OUT)
         
        self.p = GPIO.PWM(self.MotorPin, 50)

        self.p.start(7.5)
        
        print("setup complete")


    # runs all the sensors, should probably be run in a thread
    def run_ir(self):
        while True:
            if self.sensors["IR Detector"]:
                obstacle_input = GPIO.input(self.ObstaclePin)
            if (0 == obstacle_input and self.sensors["Active Buzzer"]):
                self.Buzzer.start(50)
            else:
                self.Buzzer.stop()
                
                
    def run_buzzer(self):
                self.Buzzer.start(50)
                time.sleep(2)
                self.Buzzer.stop()
                #self.sensors["Active Buzzer"] = not self.sensors["Active Buzzer"]
        

    def run_therm(self):
        status = 1
        tmp = 1
        while True:
            if self.sensors["Thermometer"]:
                temp = self._getTemp()
                if temp > 21.0:
                    self._setColor(self.colors[0])
                else:
                    self._setColor(self.colors[1])
                print ('temperature = ', temp, 'C')
                self.values["temp"] = str(temp)
                tmp = GPIO.input(16)
                if tmp != status:
                    print(tmp)
                    status = tmp
            if not self.sensors["Two Color LED"]:
                self._setColor(0x0000)
            time.sleep(1)

    def run_motor(self):
        while True:
            if self.sensors["Motor"]:
                servo.angle = self.values["angle"]
          
    def _turnRight(self):
        self.rotate(2.5)
        
    def _turnLeft(self):
        self.rotate(12.5)

    # GPIO cleanup
    def destroy(self):
        self.Buzzer.stop()
        self.p_R.stop()
        self.p_G.stop()
        GPIO.output(self.BuzzerPin, 1)
        GPIO.output(self.LedPins, GPIO.LOW)
        GPIO.cleanup()


    # math for color hex values???
    def _map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    # sets the color of the LED
    def _setColor(self, col):
        if col == 0xFF00:
            self.values["color"] = "red"
        else:
            self.values["color"] = "green"
        R_val = col >> 8
        G_val = col & 0x00FF
        R_val = self._map(R_val, 0, 255, 0, 100)
        G_val = self._map(G_val, 0, 255, 0, 100)
        self.p_R.ChangeDutyCycle(R_val) # Change duty cycle
        self.p_G.ChangeDutyCycle(G_val)

    def _getTemp(self):
        analogVal = ADC.read(1)
        Vr = 5 * float(analogVal) / 255
        Rt = 10000 * Vr / (5 - Vr)
        temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
        temp = temp - 273.15
        return temp
        
    def rotate(self, degree):
        self.p.ChangeDutyCycle(degree)
        time.sleep(2.5)
	


if __name__ == "__main__":
    sens = Sensors()
    ir_loop = Thread(target=sens.run_ir)
    ir_loop.start()
    therm_loop = Thread(target=sens.run_therm)
    therm_loop.start()
    motor_loop = Thread(target=sensor_obj.run_motor)
    motor_loop.start()
