import os
import socket


PORT = 5050
#SERVER = socket.gethostbyname(socket.gethostname() + ".local")
SERVER = "192.168.1.233"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 32
SEND_FILE_MESSAGE = "!SEND_FILE!"
OVER_MESSAGE = "!OVER!"
WORKER_MESSAGE = "!WORKER!"
BUFFER_SIZE = 1024 * 1024
FORMAT = 'utf-8'
EVAL_REQUEST_MESSAGE = "!EVALUATE!"
DISSCONNECT_MESSAGE = "!DISCONNECT!"
STILL_CONNECTED_MESSAGE = "!STILL_HERE!"
EVALUATING_MESSAGE = "!EVALUATING!"
WORKER_TIMEOUT = 180

def send_msg(msg, conn, needs_encode = False):
    if(needs_encode):
        msg = msg.encode(FORMAT)
    msg_length = str(len(msg))
    msg_length = msg_length.encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    conn.sendall(msg_length)
    conn.sendall(msg)

def recvall(conn, SIZE):
    ret = b""
    while(len(ret) < SIZE):
        ret += conn.recv(SIZE - len(ret))
    return ret

def receive_msg(conn, needs_decode = False, debug = False):
    msg_length = recvall(conn, HEADER)
    if(debug):
        print(msg_length)
    if(msg_length):
        msg_length = msg_length.decode(FORMAT)
        msg_length = int(msg_length)
        msg = recvall(conn, msg_length)
        if(debug):
            print(f"ACTUAL SIZE: {len(msg)}")
            print(msg)
        if(needs_decode):
            msg = msg.decode(FORMAT)
        return msg
    return ""

def send_file(filename, conn):
    send_msg(SEND_FILE_MESSAGE, conn, True)
    send_msg(filename, conn, True)
    send_msg(str(os.path.getsize(filename)), conn, True)
    with open(filename, "rb") as file:
        bytes_read = file.read(BUFFER_SIZE)
        while(bytes_read):
            #print(bytes_read)
            send_msg(bytes_read, conn)
            bytes_read = file.read(BUFFER_SIZE)

def receive_file(conn, debug = False):
    filename = receive_msg(conn, True, debug)
    #print(filename)
    file_size = int(receive_msg(conn, True, debug)) 
   # print(file_size)
    with open(filename, "wb") as file:
        size = 0
        while size < file_size:
            file_part = receive_msg(conn, False, debug)
            file.write(file_part)
            size += len(file_part)
            #print("SIZE until now: ", size)
            
    return filename
        
            