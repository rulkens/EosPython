#!/usr/bin/python

# ===========================================================================
# default UDP server for communicating with the EOS from outside
#
# the server interface is very simple.
#
# INIT MESSAGE
#
# Byte 1-2: 0xFE 0xF0
#
# * The server resets the counter for this address.
# * Response: 'IOK'
#
# INSTRUCTION MESSAGE
# Byte 1-2 : 0xFE 0xF1 (message start)
# Byte 3-6 : seq number
# Byte 7-8 : PWM value for light #1
# Byte 9-10: PWM value for light #2
# ...
# Byte X   : 0x00 (end)
#
# * response: if ok:
#       'MOK' & seq_number (long)
#   if not ok:
#       'MER' & error_code (byte) & seq_number (long, optional)
#
# If the messages are received out of order, the instruction with the
# highest sequence number is executed, and all others ignored. For each
# address, the server remembers the highest sequence number.
#
# NOTE: the server expects Big Endian format!!
#
# ===========================================================================


import socket
import sys
import logging
import os
from struct import *
import time
# from eos.driver.EOS_Driver import EOS_Driver

logging.getLogger().setLevel(logging.DEBUG)

# create an dictionary to remember the sequence number for each client address
seq_counters = {}

MESSAGE_INIT = '\xFE\xF0'
MESSAGE_ACTION = '\xFE\xF1'
NUM_LIGHTS = 32

ERROR_START = 'MER'   # short for MESSAGE_ERROR
ERROR_ACK = '\x01'    # the acknowledgement bytes are not valid
ERROR_SEQ = '\x02'    # seq_number is not valid (has already been used?)
ERROR_PWM = '\x03'    # PWM values are not valid
ERROR_API = '\x04'    # when something goes wrong in calling the API
ERROR_FORMAT = '\x05' # something wrong with unpacking the message

# Try to create the UDP socket
try :
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info('Socket created')
except socket.error, msg :
    logging.info('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

# mock for EOS API
def EOS_API(action, args):
    """MOCK for EOS API """
    logging.info('EOS API called with %s, %s', action, args)

def is_valid_pwm_seq(seq):
    """check if each item in the sequence is between 0 and 4095"""
    if not seq: return False
    # check if each item is between 0 and 4095
    for i in seq:
        if i < 0 or i > 4095: return False
    return True

def to_hex(val):
    """convert a value to a printable hexadecimal value"""
    return ":".join("{:02x}".format(ord(c)) for c in val)

def act_on(data, addr):
    """do something with the data"""
    if data == MESSAGE_INIT:
        # reset the counter for this address
        seq_counters[addr] = 0
        return 'IOK'

    seq_count = seq_counters[addr]
    logging.info('seq count for addr (%s, %s)' % (seq_count, addr))
    # try to make a struct out of it
    try:
        raw_msg = list(unpack('>ccL32H', data))
        msg = { 'ack': raw_msg[0] + raw_msg[1], 'seq_number': raw_msg[2], 'pwm_values': raw_msg[-NUM_LIGHTS:]}
        logging.info('message %s' % msg)
    except Exception, error_msg:
        logging.warn('unpacking message failed. Error  : %s' % error_msg)
        logging.warn(len(data))
        return ERROR_START + ERROR_FORMAT

    # already pack the sequence number, ready to be Send
    pack_seq = pack('>L', msg['seq_number'])

    # handle all sort of errors
    if msg['ack'] != MESSAGE_ACTION:
        logging.warn('ack not valid!')
        return ERROR_START + ERROR_ACK + pack_seq
    if msg['seq_number'] <= seq_count:
        logging.warn('seq_number not valid!')
        return ERROR_START + ERROR_SEQ + pack_seq
    if not is_valid_pwm_seq(msg['pwm_values']):
        logging.warn('pwm_values not valid!')
        return ERROR_START + ERROR_PWM + pack_seq

    pwm_list = msg['pwm_values']
    # call the API
    try:
        EOS_API('setRaw', pwm_list)
    except Exception, error_msg:
        logging.warn('Something went wrong in the EOS API: %s', error_msg)
        return ERROR_START + ERROR_API + pack_seq

    # set the current sequence number to the one retrieved from the message
    seq_counters[addr] = msg['seq_number']

    # return the OK message!
    return 'MOK' + pack_seq


def main():
    """main application entry point"""

    socket_port = int(os.getenv('EOS_UDP_PORT', 5155))

    # Bind socket to local host and port
    try:
        socket.bind(('', socket_port))
    except Exception, msg:
        logging.warn( 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    logging.info('listening on port %s' % socket_port)

    logging.info('Socket bind complete')

    # now keep talking with the client
    while 1:
        # receive data from client (data, addr)
        d = socket.recvfrom(1024)
        data = d[0]
        addr = d[1]

        if addr in seq_counters:
            # addr already made earlier contact
            logging.info('Address known %s' % addr[0])
        else:
            # create a new record and set it to 0
            logging.info('New client %s' % addr[0])
            seq_counters[addr] = 0

        if not data:
            break

        logging.info("Receive some data")
        logging.info(to_hex(data))

        reply = act_on(data, addr)

        socket.sendto(reply, addr)

    socket.close()


if __name__ == "__main__":
    main()
