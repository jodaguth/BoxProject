import time
import bme280
import smbus2
import threading
import pickle
import socket
import select
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas

############################################################# Declare available Buses############################
bus1 = [smbus2.SMBus(1),i2c(port=1,address=0x3c)]
bus3 = [smbus2.SMBus(3),i2c(port=3,address=0x3c)]
bus4 = [smbus2.SMBus(4),i2c(port=4,address=0x3c)]
busses = [bus1,bus3,bus4]
#################################################################################################################

############################################################## Decalare Message params ##########################
HEADERSIZE = 10
SERVER = ''
PORT = 12345
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
##################################################################################################################

############################################################### Create, set, bind and start listening ############
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(ADDR)
server.listen(5)
inputs = [server]
outputs = []
message_queues = {}
timeout = 1
###################################################################################################################

Data_on_Server = {}
BMEAVG = {}
BME280 = {}
Displays = {}
DisplayInfo = {}

# Excpected Message is Boolean|Headersize|PickledBytes
# Expected Data structure [BOX#,Display_Setting]
# Sending Out Data_on_Server[DATA|DISPLAY]
# DATA[box#][Average|Current] = [tmp,hum,press]   DISPLAY[Box#] = 'displaysetting'











def find_devices():
    boxnum = 1
    dev = 0
    dev1 = 0
    for i in busses:
        try:
            calibration_params = bme280.load_calibration_params(i[0], 0x76)
            data = bme280.sample(i[0], 0x76, calibration_params)
            dev = 1
        except:
            dev = 0
        try:
            device = ssd1306(i[1], rotate=0)
            dev1 = 1
        except:
            dev1 = 0
        if dev == 1:
            b = 'box'+ str(boxnum)
            BME280[b] = i[0]
            BMEAVG[b] = [0,0,0]
        if dev1 == 1:
            b = 'box' + str(boxnum)
            Displays[b] = device
            DisplayInfo[b] = 'stats'

        boxnum = boxnum + 1

def read_bme280(box):
    global BMEAVG
    global BME280
    if box in BME280.keys():
        bx = BME280[box]    
        calibration_params = bme280.load_calibration_params(bx, 0x76)
        data = bme280.sample(bx, 0x76, calibration_params)
        tmp,hum,pres = data.temperature,data.humidity,data.pressure
        data1 = [tmp,hum,pres]
        temp = BMEAVG[box]
        tmp1,hum1,pres1 = temp
        tmp2 = (tmp1 + tmp) / 2
        hum2 = (hum1 + hum) / 2
        pres2 = (pres1 + pres) / 2
        temp1 = [tmp2,hum2,pres2]
        BMEAVG[box] = temp1
        return data1, temp1
    else:
        return [0,0,0],[0,0,0]

def create_data():
    global Data_on_Server
    global Displays
    global DisplayInfo
    sd = {}
    for i in Displays.keys():
        d = read_bme280(i)
        sd[i] = {}
        sd[i]['current'] = d[0]
        sd[i]['average'] = d[1]
        Data_on_Server['DATA'] = sd
        #print(sd)
        Data_on_Server['DISPLAY'] = DisplayInfo

def display_out(info,box,type1):
    global Displays
    if type1 == 'stats' and info[box]['current'][0] != 0:
        info1 = info[box]['current']
        with canvas(Displays[box]) as draw:
            draw.text((1, 1),"Temperture = {:.2f}".format(info1[0]) , fill="white")
            draw.text((1, 25),"Humidity = {:.2f}".format(info1[1]), fill="white")
            draw.text((1, 50),"Pressure = {:.2f}".format(info1[2]), fill="white")
            draw.text((1, 75),"", fill="white")
    if type1 == 'average' and info[box]['current'][0] != 0:
        info2 = info[box]['average']
        with canvas(Displays[box]) as draw:
            draw.text((1, 1)," Avg T = {:.2f}".format(info2[0]) , fill="white")
            draw.text((1, 25),"Avg H = {:.2f}".format(info2[1]), fill="white")
            draw.text((1, 50),"Avg P = {:.2f}".format(info2[2]), fill="white")
            draw.text((1, 75),"", fill="white")
    if type1 == 'home' or info[box]['current'][0] == 0:
        with canvas(Displays[box]) as draw:
            draw.rectangle(Displays[box].bounding_box, outline="white", fill="black")
            draw.text((40, 20),"Hello", fill="blue")
            draw.text((15, 30),"Welcome to Home", fill="blue")
    if type1 == 'off':
         with canvas(Displays[box]) as draw:
            draw.rectangle(Displays[box].bounding_box, outline="black", fill="black")


def run_displays_data_collection():
    global DisplayInfo
    global Data_on_Server
    while True:
        create_data()
        for i in DisplayInfo:
            d1 = DisplayInfo[i]
            display_out(Data_on_Server['DATA'],i,d1)

find_devices()
dis = threading.Thread(target = run_displays_data_collection)
dis.setDaemon = True
dis.start()
while inputs:
    print('waiting on next event')
    readable, writable, exceptional = select.select(inputs, outputs,inputs,timeout)
    
    if not(readable or writable or exceptional):
        print('Time Out')
        continue

    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            print(f'new connection from {client_address}')
            connection.setblocking(0)
            inputs.append(connection)
        else:
            data = s.recv(1024)
            if data:
                print(f'received From{s.getpeername()}')
                HeaderInfo = data[:1]
                data = pickle.loads(data[10:])
                if HeaderInfo == 1:
                    Data_on_Server['DisplayInfo'][data[0]] = data[1]
                else:
                   messages_quesues[s].put(Data_on_Server)
                   if s not in outputs:
                       output.append(s)  
            else:
                print(f'Closing Client {client_address}')
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del message_queues[s]
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except Queue.Empty:
            Print('Couldnt Recieve Info wont send any')
            outputs.remove(s)
        else:
            Print(f'Sent Message to {s.getpeername()}')
            s.send(next_mesg)
    for s in exceptional:
        print(f'Handled an Error for {s.getpeername()}')
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_Queues[s]