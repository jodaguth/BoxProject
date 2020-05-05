import socket
import time
import pickle
import threading
import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.clock import Clock
import pkg_resources.py2_warn
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.window import WindowBase
import os, sys
from kivy.resources import resource_add_path, resource_find
########################################## Initialize Some Variables ##############################
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
flg = {}
####################################################################################################

Builder.load_string("""
<MainScreen>:
    
    BoxLayout:
        orientation:'vertical'
        
        BoxLayout:
            orientation: 'horizontal'
            Spinner:
                id: spinner_1
                text: 'Statistics'
                values: root.pickType
                on_text: root.updateSubSpinner(spinner_1.text)
            Spinner:
                id: spinner_2
                text: 'box1'
                values: root.pickSubType
                on_text: root.updateNewSpinner(spinner_2.text)

        
        BoxLayout:
            orientation:'horizontal'
            Label:
                id: label_temp
                text: 'Temperature'
            Label:
                id: label_tempd
                text: root.temp
                BoxLayout:
        BoxLayout:
            orientation:'horizontal'
            Label:
                id: label_hum
                text: 'Humidity'
            Label:
                id: label_humd
                text: root.hum
        BoxLayout:
            orientation:'horizontal'
            Label:
                id: label_press
                text: 'Pressure'
            Label:
                id: label_pressd
                text: root.press
        BoxLayout:
            orientation:'horizontal'
            Label:
                id: label_disp
                text: 'Currently Diplaying'
            Spinner:
                id: spinner_3
                text: ''
                values: root.disp
                on_text: root.send_mesg(spinner_2.text,spinner_3.text)

""")

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
    global Master

    while True:
        full_msg = b''
        new_msg = True
        if Master == False:
            break
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
    global Master
    while True:
        send_data('all',1)
        time.sleep(.5)
        if Master == False:
            break

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        self.buildLists()
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.updateSubSpinner,0)
    
    def buildLists(self):
        self.pickType = ['Statistics','Average','Graph']
        self.pickSubType = ['Select']
        self.temp = '0'
        self.hum = '0'
        self.press = '0'
        self.disp = ['stats','average','home','off']
    
    def updateNewSpinner(self,text):
        iii = dataIN[1]
        i = iii[text]
        ii = i[0]
        self.ids.spinner_3.text = ii

    def updateSubSpinner(self,text):
        global flg
        self.ids.spinner_2.values = names
        d = dataIN[0]
        iii = dataIN[1]
        i = iii[self.ids.spinner_2.text]
        ii = i[0]
        d = d[self.ids.spinner_2.text]
        tmp,hum,press = d[0]
        self.ids.label_tempd.text = str(round(tmp,2))
        self.ids.label_humd.text = str(round(hum,2))
        self.ids.label_pressd.text = str(round(press,2))
        if self.ids.spinner_3.text == '':
            self.updateNewSpinner(self.ids.spinner_2.text)
        else:
             self.updateNewSpinner(self.ids.spinner_2.text)


    def send_mesg(txt,txt1,txt2,*args):
        tx = str(txt1)
        tx1 = str(txt2)
        txt4 = [tx,tx1]
        send_data(txt4,0)
        dataIN[1][tx][0] = tx1

    def onExit(self):
        BoxProjectApp().stop()
        Master = False

class BoxProjectApp(App):
    global Master
    global flg
    def build(self):
        #Window.bind(on_request_close=self.on_request_close)
        return MainScreen()
    def on_request_close(self,*args):
        Master = False
        BoxProjectApp().stop()
        exit()

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    global s
    global Master
    Master = True
    connect_host()
    sti = threading.Thread(target=start_info)
    st = threading.Thread(target=get_input)
    st.daemon = True
    sti.daemon = True
    st.start()
    sti.start() 
    BoxProjectApp().run()