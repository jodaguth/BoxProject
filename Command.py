import socket
import time
import pickle
import threading
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ListProperty

##test to see commit

HEADERSIZE = 10
dataIN = [[0,0,0],0]
conn1 = 0
addr1 = 0
HEADER = 64
PORT = 12345
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '192.168.0.21'
ADDR = (SERVER, PORT)
flag1 = True
connected = False
iscon = False
names = []
name = []

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        self.buildLists()
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.updateSubSpinner,0)
    
    def buildLists(self):
        self.pickType = ['Stats','Average','Graph']
        self.pickSubType = ['Select']
        self.temp = '0'
        self.hum = '0'
        self.press = '0'
    
    def updateSubSpinner(self,text):
        self.ids.spinner_2.values = names
        d = dataIN[0]
        d = d[self.ids.spinner_2.text]
        tmp,hum,press = d[0]
        self.ids.label_tempd.text = str(tmp)
        self.ids.label_humd.text = str(hum)
        self.ids.label_pressd.text = str(press)

    def onExit(self):
        BoxProjectApp().stop()
        Master = False

class BoxProjectApp(App):
    def build(self):
        return MainScreen()

def connect_host():
    global flag1
    global iscon
    global connected
    global s
    flag1 = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while flag1 == True:
        try:
            s.connect((ADDR))
            connected = True
        except:
            print("Can't connect to host")
            ts = time.time()
        if connected == True:
            print('connected1')
            flag1 = False
            iscon = True
            flag2 = True

        else:
            while time.time() - ts <= 30 and flag1 == True:
                try:
                    s.connect((ADDR))
                    connected = True
                except:
                    connected = False
                if connected == False and time.time() - ts >=30:
                    print("Timed Out")
                    iscon = False
                    flag1 = False
                if connected == True:
                    print('Connected')
                    iscon = True
                    flag2 = True
                    flag1 = False
                    connected = True


def get_input():
    global s
    global dataIN
    global connected
    global flag2
    while True:
        full_msg = b''
        new_msg = True
        while True:
            try:
                msg = s.recv(1024)
                if new_msg:
                    msglen = int(msg[:HEADERSIZE])
                    new_msg = False

                full_msg += msg

                if len(full_msg)-HEADERSIZE == msglen:
                    dataIN = pickle.loads(full_msg[HEADERSIZE:])
                    for i in dataIN[1].keys():
                        if i in names:
                            pass
                        else:
                            names.append(i)
                    
                    new_msg = True
                    full_msg = b""
            except:
                connected = False
                flag2 = False
                iscon = False
                connect_host()

def send_data(msg1,rqst=0):
    global s
    global connected
    message = pickle.dumps(msg1)
    hdr=HEADERSIZE - 1
    rqst1 = bytes(rqst)
    #print(hdr)
    msg2 = bytes(f"{rqst}{len(message):<{hdr}}", 'utf-8') + message
    #print(msg2)
    try:
        s.send(msg2)
    except:
        print('close')
        s.close()
        connect_host()  

def start_info():
    while True:
        send_data('all',1)
        time.sleep(.1)

def run_program():
    global connected
    global iscon
    if connected == True:
        sti = threading.Thread(target=start_info)
        st = threading.Thread(target=get_input)
        st.start()
        sti.start()
        while iscon == True:
            print(dataIN[1])
            inpt = input("'display' or 'stats'")
            if inpt == 'display':
                msg1 = input('Choose a box, (box1,box2,box3)')
                msg2 = input('Choose from "stats", "average", "difference", "home", "off": \n ')
                msg = [msg1,msg2]
                send_data(msg)
            if inpt == 'stats':
                msg = input('Choose a box, (box1,box2,box3)')
                print(msg)
                send_data(msg,1)
    else:
        print('NO CONNECTION')

#if __name__ == "__main__":
    #connect_host()

    #if connected == True:
        #sti = threading.Thread(target=start_info)
        #st = threading.Thread(target=get_input)
        #st.start()
        #sti.start()
    #BoxProjectApp().run()
#while True:
    #print(dataIN[1])
    #inpt = input("'display' or 'stats'")
    #if inpt == 'display':
        #msg1 = input('Choose a box, (box1,box2,box3)')
        #msg2 = input('Choose from "stats", "average", "difference", "home", "off": \n ')
        #msg = [msg1,msg2]
        #send_data(msg)
    #if inpt == 'stats':
        #msg = input('Choose a box, (box1,box2,box3)')
        #print(msg)
        #send_data(msg,1)


if __name__ == "__main__":
    global s
    Master = True
    connect_host()
    sti = threading.Thread(target=start_info)
    st = threading.Thread(target=get_input)
    st.start()
    sti.start()  
    BoxProjectApp().run()
s.close()