##VA RULA PE SERVERUL VCODERS


import socket
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auxiliary_functions import *

start = time.time()

if len(sys.argv) != 2:
    print("INVALID NUMBER OF ARGUMENTS")
    exit()

filename = sys.argv[1]
EVAL_REQUEST_MESSAGE = "!EVALUATE!"
DISSCONNECT_MESSAGE = "!DISCONNECT!"
OVER_MESSAGE = "!OVER!"
FORMAT = 'utf-8'


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
while not connected:
    try:
        client.connect(ADDR)
        connected = True
    except:
        print(f"COULDN'T CONNECT TO MIDDLE [{ADDR}]")
        time.sleep(2)
        connected = False


send_msg(EVAL_REQUEST_MESSAGE, client, True)

send_file(filename, client)

msg = receive_msg(client, True)
if (msg == SEND_FILE_MESSAGE):
    filename = receive_file(client)

#print(time.time() - start)

client.close()

