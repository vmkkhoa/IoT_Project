print("IOT gateway")

import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import geocoder

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "Ald9ZYszVssK7fiHSRoD"
TIMER_CYCLE = 5


mess = ""
bbc_port = "COM11"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)
    


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    
    temp = 0
    light = 0  
    cmd = 0  
    led = 0
    fan = 0
    id = splitData[0] #ID of sensor
    collect_data = {'temperature1': temp,'light1': light,'temperature2': temp,'light2': light,'CMD': cmd,'LED': led,'FAN': fan}
    
    if(id == 1):
        if(splitData[1] == "TEMP"):
            temp = splitData[2]
            collect_data['temperature1']== temp
        elif(splitData[1] == "LIGHT"):
            light = splitData[2]
            collect_data['light1'] = light       
    elif(id == 2):
        if(splitData[1] == "TEMP"):
            temp = splitData[2]
            collect_data['temperature2']== temp
        elif(splitData[1] == "LIGHT"):
            light = splitData[2]
            collect_data['light2'] = light 


    if(splitData[1] == "CMD"):
        cmd = splitData[2]
        collect_data = {'CMD': cmd}
    elif(splitData[1] == "LED"):
        led = splitData[2]
        collect_data = {'LED': led}
    elif(splitData[1] == "FAN"):
        fan = splitData[2]
        collect_data = {'FAN': fan}

       
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


