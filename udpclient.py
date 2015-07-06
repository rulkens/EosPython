import socket
import sys
import logging
from struct import *
import time

logging.getLogger().setLevel(logging.DEBUG)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 5155)
MESSAGE_INIT = '\xFE\xF0'
MESSAGE_ACTION = '\xFE\xF1%s%s'

# make sure to increase this every time you send a message
# and start with 1!!
seq_number = 1

def get_pwm_values():
    # give a tiny value (255 of 4096)
    return '\x0E\xFF' * 32

def to_hex(val):
    return ":".join("{:02x}".format(ord(c)) for c in val)

def send_message(msg):
    # Send data
    logging.info('sending "%s"' % to_hex(msg))
    sent = sock.sendto(msg, server_address)

    # Receive response
    logging.info('waiting to receive')
    data, server = sock.recvfrom(4096)
    logging.info('received "%s"' % data)

    return data

def action(values):
    return MESSAGE_ACTION % (pack('>L', seq_number), get_pwm_values())

def send_values(values):
    global seq_number
    ret = send_message(action(values))
    seq_number += 1
    return ret

def send_init():
    return send_message(MESSAGE_INIT)

# MAIN
try:

    # try sending an INIT message

    send_init()
    send_values(get_pwm_values())

finally:
    logging.info('closing socket')
    sock.close()
