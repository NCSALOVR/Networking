'''
The prototype version. Please refer to ../WinCPPClient/WinCPPClient/socketHelper.cpp for the actual c++ code that is used in VIVE.
Note: There might be small differences due to different in the two languages. 
Also, there is the addition of setupClientSocket() in socketHelper.cpp 
due to the relatively complex socket creation and connection in Window C++ (i.e., socket.socket() and connect((host,port)) in python).
'''
import socket
import struct

def send_msg(conn,msg):
    bytes_send = struct.pack('!I', len(msg)) + msg
    conn.sendall(bytes_send)

def recv_msg(conn):
    msg_len = struct.unpack('!I', recv_num_bytes(conn, struct.calcsize('!I')))[0]
    return recv_num_bytes(conn, msg_len)

def recv_num_bytes(conn, num_bytes):
    recv_data = ''
    while len(recv_data) < num_bytes:
        curr_recv = conn.recv(num_bytes-len(recv_data))
        recv_data = recv_data + curr_recv
    return recv_data

