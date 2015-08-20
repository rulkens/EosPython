import socket
import sys
import logging
from struct import *
import time

logging.getLogger().setLevel(logging.DEBUG)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 5155)
MESSAGE_INIT =      '\xFE\xF0'
MESSAGE_HALOGEN =   '\xFE\xF1%s%s'
MESSAGE_LED =       '\xFE\xF2%s%s'

# make sure to increase this every time you send a message
# and start with 1!!
seq_number = 1

def get_pwm_values():
    # give a tiny value (255 of 4096)
    return '\x0E\xFF' * 32

def get_led_values():
    # red
    return '\x00\xFF\x00\x00' * 120

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

def halogens(values):
    return MESSAGE_HALOGEN % (pack('>L', seq_number), values)

def leds(values):
    return MESSAGE_LED % (pack('>L', seq_number), values)

def send_values(values):
    global seq_number
    ret = send_message(halogens(values))
    seq_number += 1
    return ret

def send_led_values(values):
    global seq_number
    ret = send_message(leds(values))
    seq_number += 1
    return ret

def send_init():
    return send_message(MESSAGE_INIT)

# MAIN
try:

    # try sending an INIT message

    send_init()

    send_led_values('\x00\xFF\x00\x00' * 120)
    time.sleep(.5)
    send_led_values('\x00\x00\xFF\x00' * 120)
    time.sleep(.5)
    send_led_values('\x00\x00\x00\xFF' * 120)
    time.sleep(2)

    # all off
    send_led_values('\x00\x00\x00\x00' * 120)


    send_values(get_pwm_values())
    time.sleep(6)
    send_values('\x00\x00' * 32)
    time.sleep(3)



finally:
    logging.info('closing socket')
    sock.close()
