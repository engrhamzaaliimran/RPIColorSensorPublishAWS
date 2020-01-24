import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import RPi.GPIO as GPIO
from gpiozero import LED
from time import sleep
import time
import json

s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):
    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("red: " + str(payloadDict["state"]["reported"]["red"]))
        print("blue: " + str(payloadDict["state"]["reported"]["blue"]))
        print("green: " + str(payloadDict["state"]["reported"]["green"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

# Function called when a shadow is deleted
def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


def loop():
  color="No Color"
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(s2,GPIO.OUT)
  GPIO.setup(s3,GPIO.OUT)
  
  # Make sure that Client ID is unique for each device
  myAWSIoTMQTTShadowClient = AWSIoTPyMQTT.AWSIoTMQTTShadowClient("RPIColorSensor")
  myAWSIoTMQTTShadowClient.configureEndpoint("a1161nszd8qg24-ats.iot.eu-west-3.amazonaws.com", 8883)
  myAWSIoTMQTTShadowClient.configureCredentials("root-ca.pem", "rpi-private.pem.key", "rpi-certificate.pem.crt")
  
  print(myAWSIoTMQTTShadowClient.connect())
  
  BotShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("RPI3", True)
  
  print("\n")
  while(1):
    print (" --- Reading Values ---")
    GPIO.output(s2,GPIO.LOW)
    GPIO.output(s3,GPIO.LOW)
    time.sleep(0.3)
    start = time.time()

    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start      #seconds to run for loop
    red  = NUM_CYCLES / duration   #in Hz
    print("red value - ",red)
    if(red>25000):
      color="Red"
    GPIO.output(s2,GPIO.LOW)
    GPIO.output(s3,GPIO.HIGH)
    time.sleep(0.3)

    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    blue = NUM_CYCLES / duration
    print("blue value - ",blue)
    if(blue>27000):
      color="Blue"

    GPIO.output(s2,GPIO.HIGH)
    GPIO.output(s3,GPIO.HIGH)
    time.sleep(0.3)

    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    green = NUM_CYCLES / duration
    print("green value - ",green)
    if(green>27000):
      color="Green"
    if(green>22000 and blue<25000):
      color="Green"

    if( (red<19000) and (green<19000) and (blue<19000) ) :
      color="NoColor"
    # Create message payload
    print(color)
    payload = {"state":{"reported":{"red":str(red),"blue":str(blue),"green":str(green),"color":str(color)}}}
    

    try:
       #Updating Device Shadow
       print(BotShadow.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 2))
       time.sleep(2)
    except: 
       print("Error Connecting to AWS IOT")


def endprogram():
    GPIO.cleanup()

if __name__=='__main__':
    try:
        loop()
    except KeyboardInterrupt:
        endprogram()

