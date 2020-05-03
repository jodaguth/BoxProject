import socket
import time
import pickle
import threading
import kivy
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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ADDR))

def get_input():
    global s
    global dataIN
    while True:
        full_msg = b''
        new_msg = True
        while True:
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

def send_data(msg1,rqst=0):
    global s
    message = pickle.dumps(msg1)
    hdr=HEADERSIZE - 1
    rqst1 = bytes(rqst)
    #print(hdr)
    msg2 = bytes(f"{rqst}{len(message):<{hdr}}", 'utf-8') + message
    #print(msg2)
    s.send(msg2)
def start_info():
    while True:
        send_data('all',1)
        time.sleep(1)
sti = threading.Thread(target=start_info)
st = threading.Thread(target=get_input)
st.start()
sti.start()

while True:
    print(dataIN[1])
    inpt = input("'display' or 'stats'")
    if inpt == 'display':
        msg1 = input('Choose a box, (box1,box2,box3)')
        msg2 = input('Choose from "stats", "average", "difference", "home", "off": \n ')
        msg = [msg1,msg2]
        send_data(msg)
    if inpt == 'stats':
        msg = input('Choose a box, (box1,box2,box3)')
        #print(msg)
        send_data(msg,1)
