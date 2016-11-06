#!/usr/bin/python
# ===========================================================================
# default UDP server for touch button events
#
import socket
import os
import serial
import time
import logging
import Queue
import threading
import signal
import sys
import random

# wait while the arduino resets

## touch types
TT_OFF = 1
TT_ON  = 0
TT_L   = 2
TT_XL  = 3

# IP to send to
address = ('127.0.0.1',0)

# create an dictionary to remember the sequence number for each client address
seq_counters = {}

# serial setup
BAUD_RATE = 19200

## states
STATE = {'SETUP' : 0, 'STARTUP' : 1, 'OK' : 2, 'ERROR' : 3, 'PROG_RUN' : 4, 'TOUCH' : 10, 'TOUCH_LONG' : 11, 'TOUCH_XLONG' : 12}
# init messages
INIT = 'INIT'

queue = Queue.Queue()
out_queue = Queue.Queue()

# TODO: make this auto-detecting?
ser = serial.Serial('/dev/ttyUSB0', BAUD_RATE)

# Try to create the UDP socket
try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #socket.setblocking(0) # non-blocking socket
    logging.info('Socket created')
except socket.error, msg :
    logging.info('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()


last_tap_time = 0
prevent_tap = False

# send a message to the client(s)
def send(message):
    socket.sendto(message, address)

def handle_signal(sig, frame):
    logging.info('stopping')
    t_serial.stop()
    ser.close()
    socket.close()
    running = False
    #t_serial.join()
    sys.exit()

def on_tap(data):
    global last_tap_time, prevent_tap
    # logging.info('tapped')
    # time_since_last_tap = time.time() - last_tap_time
    # logging.info('time last tap %s' % time_since_last_tap)
    # if time_since_last_tap > .9 and not prevent_tap:
    #     # only set when we have a longer timeout
    #     EOS_API('light', ['.7', '2.5', '0.5', 'cube'])
    #     set_state('PROG_RUN')
    #
    # prevent_tap = False
    # last_tap_time = time.time()
    send('TAP')

def on_doubletap(data):
    #global prevent_tap
    logging.info('double tapped')
    #EOS_API('light', ['.7', '5.5', '1.0', 'cube'])
    #prevent_tap = True
    #set_state('PROG_RUN')
    send('DOUBLE_TAP')

def on_touch_off():
    logging.info('touch off')
    send('TOUCH_END')

def on_touch_on():
    global touch_time, touch_started
    logging.info('touch on')
    send('TOUCH_START')

def on_touch_l():
    logging.info('touch long')
    send('TOUCH_L')

def on_touch_xl():
    global prevent_tap
    logging.info('touch extra long')
    # end the app?
    # turn off all lights

    # # TODO: call TCP
    # EOS_API('alloff')
    # prevent_tap = True
    # set_state('OK')
    send('TOUCH_XL')

def set_state(state):
    try:
        s = str(STATE[state])
        ser.write('setState ' + s)
    except Exception:
        logging.info('[ERROR] cant set state %s' % state)
        send('ERROR')


def act_on(data):
    if data == 'INIT':
        return 'INIT_OK'

    # try to split
    commands = data.split()

    if commands[0] == 'SET_STATE':
        # set state
        set_state(commands[1])
        return 'STATE_SET ' + commands[1]

    return 'OK'

def server_loop():
    global address
    # now keep talking with the client
    while 1:
        # receive data from client (data, addr)
        #t0 = time.time()
        try:
            d = socket.recvfrom(512)
        except Exception:
            # no data here
            logging.info('[ERROR] cant receive from socket')
            continue

        data = d[0]
        addr = d[1]

        # set the ip to send to
        address = addr

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
        #logging.info(data)

        # send hello world reply from API to client
        socket.sendto(act_on(data), address)

        total_dropped = 0
        # empty data in socket
        while 0:
            inputready, o, e = select.select([socket],[],[], 0.0)
            if len(inputready) == 0:
                break
            for s in inputready:
                s.recv(1)
                total_dropped += 1
                # logging.info('dropping %s' % total_dropped )

#class SerialServer(TCPServer):

class SerialThread(threading.Thread):
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        logging.info('start listening to serial events')
        while True :
            # stop listening in case we get a stop event
            if self.stopped():
                logging.info('stopping serial thread')
                break

            ret = ser.readline()

            #place chunk into out queue
            #self.out_queue.put(chunk)
            logging.info('receiving %s', ret)
            # split on comments
            if ret[0] == '#':
                # it's a comment
                # ignore it
                #logging.info('comment')
                void = 0
            else:
                #print(ret)
                #logging.info('command', ret)
                # split
                res = ret.strip().split(' ')

                if res[0] == 'event':
                    print res
                    type = res[1]
                    #print('event')
                    if type == 'tap':
                        on_tap(res[2])
                    if type == 'doubletap':
                        on_doubletap(res[2])
                    #logging.info('event', res)
                    if type == 'touch':
                        touch_type = int(res[2])
                        if touch_type == TT_ON:
                            on_touch_on()
                        if touch_type == TT_OFF:
                            on_touch_off()
                        if touch_type == TT_L:
                            on_touch_l()
                        if touch_type == TT_XL:
                            on_touch_xl()

        logging.info('listening ended')
        #self.exit()

t_serial = SerialThread(queue, out_queue)

def main():
    # main entry point
    logging.info('[TOUCH] started!')
    logging.getLogger().setLevel(logging.DEBUG)

    socket_port = int(os.getenv('EOS_TOUCH_PORT', 5158))
    logging.info('listening on port %s' % socket_port)

    # Bind socket to local host and port
    try:
        socket.bind(('', socket_port))
    except Exception, msg:
        logging.warn( 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    # start the serial listener thread
    t_serial.setDaemon(True)
    t_serial.start()

    #t_error.setDaemon(True)
    #t_error.start()

    # setup signal handling
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    running = True

    # start the server loop
    server_loop()

    socket.close()

if __name__ == "__main__":
    main()
