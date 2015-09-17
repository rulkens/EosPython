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
import select
import sys
import logging
import os
from struct import *
import time
# uses the low-level eos driver instead of the EOS_API for maximum performance
from eos.driver.EOS_Driver import EOS_Driver
from eos.driver.EOS_LEDDriver import EOS_LEDDriver

logging.getLogger().setLevel(logging.DEBUG)

# create an dictionary to remember the sequence number for each client address
seq_counters = {}

MESSAGE_INIT =      '\xFE\xF0'
MESSAGE_HALOGEN =   '\xFE\xF1'
MESSAGE_LED =       '\xFE\xF2'
MESSAGE_PANIC =     '\xFE\xFF' # panic, turn everything off

NUM_HALOGEN_LIGHTS = 32
NUM_LED_LIGHTS = 120

ERROR_START = 'MER'   # short for MESSAGE_ERROR
ERROR_ACK = '\x01'    # the acknowledgement bytes are not valid
ERROR_SEQ = '\x02'    # seq_number is not valid (has already been used?)
ERROR_PWM = '\x03'    # PWM values are not valid

ERROR_H_API = '\x04'  # when something goes wrong in calling the halogen API
ERROR_H_FORMAT = '\x05' # something wrong with unpacking the message

ERROR_L_API = '\x06'  # when something goes wrong calling the LED API
ERROR_L_FORMAT = '\x07' # something wrong with unpacking the LED message

ERROR_PANIC = '\xFF' # panic mode doesn't work??

# Try to create the UDP socket
try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.setblocking(0)
    logging.info('Socket created')
except socket.error, msg :
    logging.info('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

# Try to create Driver
try:
    eos = EOS_Driver()
except Exception, e:
    logging.warn('Failed to initialize halogen driver. Exiting!')
    sys.exit()

try:
    eosled = EOS_LEDDriver()
except Exception, e:
    logging.warn('Failed to initialize LED driver. Exiting!')
    sys.exit()


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
        logging.info('INIT OK %s' % addr)
        return 'IOK'

    seq_count = seq_counters[addr]
    #logging.info('seq count for addr (%s, %s)' % (seq_count, addr))

    ack = (data[0] + data[1])

    # check if ack is valid
    if ack != MESSAGE_HALOGEN and ack != MESSAGE_LED and ack != MESSAGE_PANIC:
            logging.warn('ack not valid!')
            return ERROR_START + ERROR_ACK

    if ack == MESSAGE_PANIC :
        try:
            eosled.allOff()
            eos.allOff()
            return 'MOK'
        except Exception, error_msg:
            logging.warn('Something went wrong in the EOS LED API: %s', error_msg)
            return ERROR_START + ERROR_PANIC + pack_seq

    # HALOGEN LIGHT PARSING
    if ack == MESSAGE_HALOGEN :
        # try to make a struct out of it
        try:
            raw_msg = list(unpack('>ccL' + str(NUM_HALOGEN_LIGHTS) + 'H', data))
            msg = { 'ack': raw_msg[0] + raw_msg[1], 'seq_number': raw_msg[2], 'light_values': raw_msg[-NUM_HALOGEN_LIGHTS:]}
            #logging.info('message %s' % msg)
        except Exception, error_msg:
            logging.warn('unpacking message failed. Error  : %s' % error_msg)
            logging.warn(len(data))
            return ERROR_START + ERROR_H_FORMAT

    # LED LIGHT PARSING
    if ack == MESSAGE_LED :
        # try to make a struct out of it
        try:
            # a LOT more data than the halogen lights
            raw_msg = list(unpack('>ccL' + str(NUM_LED_LIGHTS) + 'L', data))
            msg = { 'ack': raw_msg[0] + raw_msg[1], 'seq_number': raw_msg[2], 'light_values': raw_msg[-NUM_LED_LIGHTS:]}
            #logging.info('message %s' % msg)
        except Exception, error_msg:
            logging.warn('unpacking message failed. Error  : %s' % error_msg)
            logging.warn(len(data))
            return ERROR_START + ERROR_L_FORMAT

    # already pack the sequence number, ready to be Send
    try:
        pack_seq = pack('>L', msg['seq_number'])
    except Exception, error_msg:
        logging.warn('setting sq_number failed, Error : %s' % error_msg)
        return ERROR_START + ERROR_SEQ

    # handle all sort of errors

    if msg['seq_number'] <= seq_count:
        logging.warn('seq_number not valid!')
        return ERROR_START + ERROR_SEQ + pack_seq
    if not is_valid_pwm_seq(msg['light_values']) and ack == MESSAGE_HALOGEN:
        logging.warn('pwm_values not valid!')
        return ERROR_START + ERROR_PWM + pack_seq

    light_values = msg['light_values']

    # call the API
    if ack == MESSAGE_HALOGEN :
        try:
            eos.setRaw(light_values)
        except Exception, error_msg:
            logging.warn('Something went wrong in the EOS Halogen API: %s', error_msg)
            return ERROR_START + ERROR_H_API + pack_seq

    if ack == MESSAGE_LED :
        try:
            eosled.set(light_values)
        except Exception, error_msg:
            logging.warn('Something went wrong in the EOS LED API: %s', error_msg)
            return ERROR_START + ERROR_L_API + pack_seq



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
        try:
            d = socket.recvfrom(1024)
        except Exception:
            # no data here
            continue

        data = d[0]
        addr = d[1]

        if addr[0] in seq_counters:
            # addr already made earlier contact
            #logging.info('Address known %s' % addr[0])
            x = 1
        else:
            # create a new record and set it to 0
            logging.info('New client %s' % addr[0])
            seq_counters[addr[0]] = 0

        if not data:
            break

        #logging.info("Receive some data")
        #logging.info(to_hex(data))

        reply = act_on(data, addr[0])

        socket.sendto(reply, addr)

        # empty data in socket
        while 1:
            inputready, o, e = select.select([socket],[],[], 0.0)
            if len(inputready)==0: break
            for s in inputready: s.recv(1)

    socket.close()


if __name__ == "__main__":
    main()
