import time
import bme280
import smbus2
import threading
import pickle
import socket
import select
import queue
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
timeout = 60
timeout1 = 1
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
            BMEAVG[b] = [[0],[0],[0]]
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
        try:
            calibration_params = bme280.load_calibration_params(bx, 0x76)
            data = bme280.sample(bx, 0x76, calibration_params)
        except:
            return [0,0,0],[1,1,1]
        else:
            tmp,hum,pres = data.temperature,data.humidity,data.pressure
            data1 = [tmp,hum,pres]
            temp = BMEAVG[box]
            tmp1,hum1,pres1 = temp
            if len(tmp1) == 518400:
                tmp1 = tmp1[:-1]
                hum1 = hum1[:-1]
                pres1 = pres1[:-1]
            tmp1.append(tmp)
            hum1.append(hum)
            pres1.append(pres)
            BMEAVG[box] = [tmp1,hum1,pres1]
            tmp2 = sum(tmp1) / len(tmp1)
            hum2 = sum(hum1) / len(hum1)
            pres2 = sum(pres1) / len(pres1)
            temp1 = [tmp2,hum2,pres2]
        return [data1, temp1]
    else:
        return [0,0,0],[1,1,1]

def create_data():
    global Data_on_Server
    global Displays
    global DisplayInfo
    sd = {}
    sd['current'] = {}
    sd['average'] = {}
    for i in Displays.keys():
        d = read_bme280(i)
        sd['current'][i] = d[0]
        sd['average'][i] = d[1]
    Data_on_Server['DATA'] = sd
        #print(sd)
    Data_on_Server['DISPLAY'] = DisplayInfo

def display_out(info,box,type1):
    global Displays
    if type1 == 'stats' and info['current'][box][0] != 0:
        info1 = info['current'][box]
        try:
            with canvas(Displays[box]) as draw:
                draw.text((1, 1),"Temperture = {:.2f}".format(info1[0]) , fill="white")
                draw.text((1, 25),"Humidity = {:.2f}".format(info1[1]), fill="white")
                draw.text((1, 50),"Pressure = {:.2f}".format(info1[2]), fill="white")
                draw.text((1, 75),"", fill="white")
                except:
                    pass
    if type1 == 'average' and info['current'][box][0] != 0:
        info2 = info['average'][box]
        try:
            with canvas(Displays[box]) as draw:
                draw.text((1, 1)," Avg T = {:.2f}".format(info2[0]) , fill="white")
                draw.text((1, 25),"Avg H = {:.2f}".format(info2[1]), fill="white")
                draw.text((1, 50),"Avg P = {:.2f}".format(info2[2]), fill="white")
                draw.text((1, 75),"", fill="white")
                except:
                    pass
    if type1 == 'home' and info['current'][box][0] != 0:
        try:
            with canvas(Displays[box]) as draw:
                draw.rectangle(Displays[box].bounding_box, outline="white", fill="black")
                draw.text((40, 20),"Hello", fill="blue")
                draw.text((15, 30),"Welcome to Home", fill="blue")
    if info['current'][box][0] == 0 and type1 != 'off':
        try:
            with canvas(Displays[box]) as draw:
                draw.rectangle(Displays[box].bounding_box, outline="white", fill="black")
                draw.text((40, 20),"Hello", fill="blue")
                draw.text((15, 30),"Check Your Sensor", fill="blue")
                except:
                    pass
    if type1 == 'off':
         try:
            with canvas(Displays[box]) as draw:
                draw.rectangle(Displays[box].bounding_box, outline="black", fill="black")
                except:
                    pass


def run_displays_data_collection():
    global DisplayInfo
    global Data_on_Server
    run = True
    while run == True:
        create_data()
        time.sleep(.5)
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
    readable, writable, exceptional = select.select(inputs, outputs,inputs,timeout1)
    if not(readable or writable or exceptional):
        print('Time Out')
        continue

    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            print(f'new connection from {client_address}')
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = queue.Queue()
        else:
            try:
                data = s.recv(1024)
            except:
                print(f'Closing Client {client_address}')
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del message_queues[s]
            else:
                if data:
                    print(f'received From{s.getpeername()}')
                    HeaderInfo = int(data[:1])
                    data = pickle.loads(data[10:])
                    #print(data)
                    if HeaderInfo == 1:
                        Data_on_Server['DISPLAY'][data[0]] = data[1]
                    else:
                        dos = pickle.dumps(Data_on_Server)
                        message_queues[s].put(dos)
                        if s not in outputs:
                            outputs.append(s)  
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
        except queue.Empty:
            print('Couldnt Recieve Info wont send any')
            outputs.remove(s)
        else:
            print(f'Sent Message to {s.getpeername()}')
            s.send(next_msg)
            #print(pickle.loads(next_msg))
    for s in exceptional:
        print(f'Handled an Error for {s.getpeername()}')
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_Queues[s]