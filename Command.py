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
flag1 = True
flag2 = True
connected = False
iscon = False

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



#class BoxProjectApp(App):
    #pass


def get_input():
    global s
    global dataIN
    global connected
    global flag2
    while flag2 == True:
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
                    #print(data)
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
        time.sleep(1)

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

if __name__ == "__main__":
    #BoxProjectApp().run()
    connect_host()
    run_program()

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
