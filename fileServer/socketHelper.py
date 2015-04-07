import socket
import struct

def send_msg(conn,msg):
    bytes_send = struct.pack('!I', len(msg)) + msg
    try:
        conn.sendall(bytes_send)
    except:
        return False
    return True

def recv_msg(conn):
    msg_len = struct.unpack('!I', recv_num_bytes(conn, struct.calcsize('!I')))[0]
    return recv_num_bytes(conn, msg_len)

def recv_num_bytes(conn, num_bytes):
    recv_data = ''
    while len(recv_data) < num_bytes:
        curr_recv = conn.recv(num_bytes-len(recv_data))
        recv_data = recv_data + curr_recv
    return recv_data

