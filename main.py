print("IOT gateway")

from operator import le
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import geocoder

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "Ald9ZYszVssK7fiHSRoD"
TIMER_CYCLE = 5

temp1 = 0
light1 = 0 
temp2 = 0
light2 = 0 
cmd = 0  
led = 0
fan = 0


mess = ""
bbc_port = "COM13"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)
    


def processData(data):
    global temp1,temp2,light1,light2,cmd,led,fan
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    

    id = splitData[0] #ID of sensor
    
    if id == "1":    #data from sensor 1
        if(splitData[1] == "TEMP"):
            temp1 = splitData[2]
        elif(splitData[1] == "LIGHT"):
            light1 = splitData[2]
    elif id == "2":  #data from sensor 2
        if(splitData[1] == "TEMP"):
            temp2 = splitData[2] 
        elif(splitData[1] == "LIGHT"):
            light2 = splitData[2]

    if(splitData[1] == "CMD"):
        cmd = splitData[2]
    elif(splitData[1] == "LED"):
        led = splitData[2]  
    elif(splitData[1] == "FAN"):
        fan = splitData[2]

    #print(str(temp1) +" "+str(temp2)+" "+str(light1)+" "+str(light2)+" "+str(cmd)+" "+str(led)+" "+str(fan))
    collect_data = {'temperature1': temp1,'light1': light1,'temperature2': temp2,'light2': light2,'CMD': cmd,'LED': led,'FAN': fan}       
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]



def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 1
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":   
            if (jsonobj['params'] == True):
                cmd = 1
            else:
                cmd = 2        
            temp_data['value'] = jsonobj['params']                        
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            
        elif jsonobj['method'] == "setFAN":  
            if (jsonobj['params'] == True):
                cmd = 3
            else:
                cmd = 4  
            temp_data['value'] = jsonobj['params']          
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

counter = TIMER_CYCLE

while True:    
    if len(bbc_port) >  0:
        readSerial()
    time.sleep(1)


