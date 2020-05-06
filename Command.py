import socket
import time
import pickle
import threading
#from kivy.app import App
#from kivy.uix.floatlayout import Floatlayout
#from kivy.uix.boxlayout import Boxlayout
#from kivy.uix.textinput import TextInput
#from kivy.uix.spinner import Spinner
##test to see commit

HEADERSIZE = 10
dataIN = [0,0]
conn1 = 0
addr1 = 0
HEADER = 64
PORT = 12345
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '192.168.0.21'
ADDR = (SERVER, PORT)
Data_on_Server = {}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Connections = False





def connect_host(rep=0):
    rep1 = 0
    while rep1 <= rep:
        try:
            s.connect((ADDR))           
        except:
            rep1 += rep1
            return False
        else:
            Connections == True
            return True
            rep1 = rep
        if rep != 0:
            time.sleep(1)

def manage_data(msg1,rqst=0):
    global s
    global Data_on_Server
    global Connections
    message = pickle.dumps(msg1)
    msg2 = bytes(f"{rqst:<{10}}", 'utf-8') + message
    try:
        s.send(msg2)
    except:
        print('close')
        s.close()
        Connections == False
    else:
        if rqst == 0:
            try:
                data = s.recv(4096)
            except:
                s.close()
                Connections == False
            else:
                Data_on_Server = pickle.loads(data)

def send_display(box,disp):
    manage_data([box,disp],1)

def recieve_data():
    manage_data('')
    print(Data_on_Server)

if connect_host() == True:
    while True:
        if Connections == False:
            connect_host(5)
        in1 = input('Choose')
        if in1 == 'send':
            in2 = input('box')
            in3 = input('disp')
            send_display(in2,in3)
        if in1 == 'recv':
            recieve_data()