import time
import bme280
import smbus2
import threading
import pickle
import socket
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas

bus1 = [smbus2.SMBus(1),i2c(port=1,address=0x3c)]
bus3 = [smbus2.SMBus(3),i2c(port=3,address=0x3c)]
bus4 = [smbus2.SMBus(4),i2c(port=4,address=0x3c)]
busses = [bus1,bus3,bus4]
BME280 = {}
Displays = {}
BMEAVG = {}
Displayssetting = {}
global_data = {}
HEADERSIZE = 10
SERVER = ''
PORT = 12345
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ADDR))
Flag = 1


def handle_client(conn, addr):
    global Displayssetting
    global i
    global global_data
    connected = True
    global dataIN
    while connected ==True:
        full_msg = b''
        new_msg = True
        while connected == True:
            try:
                msg = conn.recv(1024)
                if new_msg:
                    msglen = int(msg[1:HEADERSIZE])
                    msglen1 = len(str(msglen))
                    headr = msg[:1]
                    headr1 = int(headr)
                    #rint(headr1)
                    #print(msglen)
                    new_msg = False

                full_msg += msg

                if len(full_msg)-HEADERSIZE == msglen:
                    dataIN = pickle.loads(full_msg[HEADERSIZE:])    
                    new_msg = True
                    full_msg = b""
                    if headr1 == False:
                        Displayssetting[dataIN[0]] = dataIN[1]
                        #print('Display Data')
                        #print(Displayssetting)
                    if headr1 == True:
                        #print(dataIN)
                        if dataIN == 'all':
                            msgg = [global_data,Displayssetting]
                        else: 
                            msgg = global_data[dataIN]
                        Send_msg(msgg,conn,addr)
            except:
                print('Connection with client lost')
                connected = False

    try:
        conn.close()
    except:
        pass

def Start_Server():
    s.listen()
    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr} has been established.")
        thread = threading.Thread(target=handle_client,args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")

def Send_msg(msg1,conn1,addr=0):
    message = pickle.dumps(msg1)
    msg2 = bytes(f"{len(message):<{HEADERSIZE}}", 'utf-8') + message
    print(f'message sent to{addr}')
    conn1.send(msg2)

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
            global_data[b] = 0
        if dev1 == 1:
            b = 'box' + str(boxnum)
            Displays[b] = device
            Displayssetting[b] = 'stats'

        boxnum = boxnum + 1
    return [BME280,Displays]

def read_bme280(box):
    global BMEAVG
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
        return data1,temp1
    else:
        return 0,0

def display_out(info,box,type1):
    if type1 == 'stats' and info[0] != 0:
        info1 = info[0]
        with canvas(Displays[box]) as draw:
            draw.text((1, 1),"Temperture = {:.2f}".format(info1[0]) , fill="white")
            draw.text((1, 25),"Humidity = {:.2f}".format(info1[1]), fill="white")
            draw.text((1, 50),"Pressure = {:.2f}".format(info1[2]), fill="white")
            draw.text((1, 75),"", fill="white")
    if type1 == 'average' and info[0] != 0:
        info2 = info[1]
        with canvas(Displays[box]) as draw:
            draw.text((1, 1)," Avg T = {:.2f}".format(info2[0]) , fill="white")
            draw.text((1, 25),"Avg H = {:.2f}".format(info2[1]), fill="white")
            draw.text((1, 50),"Avg P = {:.2f}".format(info2[2]), fill="white")
            draw.text((1, 75),"", fill="white")
    if type1 == 'home' or info[0] == 0:
        with canvas(Displays[box]) as draw:
            draw.rectangle(Displays[box].bounding_box, outline="white", fill="black")
            draw.text((40, 20),"Hello", fill="blue")
            draw.text((15, 30),"Welcome to Home", fill="blue")
    if type1 == 'off':
         with canvas(Displays[box]) as draw:
            draw.rectangle(Displays[box].bounding_box, outline="black", fill="black")

find_devices()
i = threading.Thread(target=Start_Server)
i.start()
while True:
    for i in Displayssetting:
        global_data[i] = read_bme280(i)
        d1 = Displayssetting[i]
        display_out(global_data[i],i,d1)