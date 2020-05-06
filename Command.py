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
Data_on_Server = {}

Data_on_Client = {}
Data_on_Client['DATA'] = {}
Data_on_Client['DISPLAY'] = {}
Data_on_Client['DATA']['average'] = {}
Data_on_Client['DATA']['current'] = {}

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
                Data_on_Server1 = pickle.loads(data)
                for i in Data_on_Server1['DATA']['current']:
                    Data_on_Client['DATA']['current'][i] = Data_on_Server1['DATA']['current'][i]
                for i in Data_on_Server1['DATA']['average']:
                    Data_on_Client['DATA']['average'][i] = Data_on_Server1['DATA']['average'][i]
                for i in Data_on_Server1['DISPLAY']:
                    Data_on_Client['DISPLAY'][i] = Data_on_Server1['DISPLAY'][i]

def send_display(box,disp):
    manage_data([box,disp],1)

def recieve_data():
    manage_data('')

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        self.buildLists()
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.updateSubSpinner,0)
        Clock.schedule_interval(self.get_data,0.5)
    
    def buildLists(self):
        self.pickType = ['Statistics','Average','Graph']
        self.pickSubType = ['Select']
        self.temp = '0'
        self.hum = '0'
        self.press = '0'
        self.disp = ['stats','average','home','off']
    
    def updateNewSpinner(self,text):
        global Data_on_Server
        i = Data_on_Client['DISPLAY'][text]
        self.ids.spinner_3.text = i

    def get_data(self,*args):
        global Data_on_Server
        global Data_on_Client
        recieve_data()

    def updateSubSpinner(self,text):
        global Data_on_Client
        names =[]
        for i in Data_on_Client['DISPLAY']:
            names.append(i)
        self.ids.spinner_2.values = names
        if self.ids.spinner_1.text == 'Statistics':
            tmp,hum,press = Data_on_Client['DATA']['current'][self.ids.spinner_2.text]
        if self.ids.spinner_1.text == 'Average':
            tmp,hum,press = Data_on_Client['DATA']['average'][self.ids.spinner_2.text]
        if self.ids.spinner_1.text == 'Graph':
            tmp,hum,press = [0,0,0]

        self.ids.label_tempd.text = str(round(tmp,2))
        self.ids.label_humd.text = str(round(hum,2))
        self.ids.label_pressd.text = str(round(press,2))
        self.updateNewSpinner(self.ids.spinner_2.text)


    def send_mesg(txt,txt1,txt2,*args):
        global Data_on_Client
        bx = str(txt1)
        tx1 = str(txt2)
        send_display(bx,tx1)
        Data_on_Client['DISPLAY'][bx] = tx1

    def onExit(self):
        BoxProjectApp().stop()

class BoxProjectApp(App):
    global Data_on_Server
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    if connect_host() == True:
        recieve_data()
        BoxProjectApp().run()