import serial
import time
import logging
import Queue
import threading
import signal
import sys
import random
from eos.api.EOS_API import EOS_API

# wait while the arduino resets

## touch types
TT_OFF = 0
TT_ON  = 1
TT_L   = 2
TT_XL  = 3

# serial setup
BAUD_RATE = 19200

## states
STATE = {'SETUP' : 0, 'STARTUP' : 1, 'OK' : 2, 'ERROR' : 3, 'PROG_RUN' : 4, 'TOUCH' : 10, 'TOUCH_LONG' : 11, 'TOUCH_XLONG' : 12}

queue = Queue.Queue()
out_queue = Queue.Queue()

ser = serial.Serial('/dev/ttyUSB0', BAUD_RATE)

last_tap_time = 0
prevent_tap = False

def handle_signal(sig, frame):
    logging.info('stopping')
    t_serial.stop()
    ser.close()
    running = False
    #t_serial.join()
    sys.exit()

def on_tap(data):
    global last_tap_time, prevent_tap
    logging.info('tapped')
    time_since_last_tap = time.time() - last_tap_time
    logging.info('time last tap %s' % time_since_last_tap)
    if time_since_last_tap > .9 and not prevent_tap:
        # only set when we have a longer timeout
        EOS_API('light', ['.7', '2.5', '0.5', 'cube'])
        time.sleep(.05)
        #set_state('PROG_RUN')

    prevent_tap = False
    last_tap_time = time.time()

def on_doubletap(data):
    global prevent_tap
    logging.info('double tapped')
    EOS_API('light', ['.7', '5.5', '1.0', 'cube'])
    prevent_tap = True
    time.sleep(.05)
    #set_state('PROG_RUN')

def on_touch_off():
    logging.info('touch off')

def on_touch_on():
    logging.info('touch on')

def on_touch_l():
    logging.info('touch long')

def on_touch_xl():
    global prevent_tap
    logging.info('touch extra long')
    # end the app?
    # turn off all lights
    EOS_API('alloff')
    prevent_tap = True
    time.sleep(4)
    #set_state('OK')

def set_state(state):
    ser.write('setState ' + str(STATE[state]))

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
            # logging.info(ret)
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
                    #print res
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

class RandomErrorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        logging.info('random error thread __init')

    def run(self):
        # start firing events only after a couple of seconds
        time.sleep(5)
        while True:
            time.sleep(random.randint(5,10))
            logging.info('setting error state')
            ser.write('setState ' + str(STATE['ERROR']))
            time.sleep(2)
            # return to ok state after 2 sec
            ser.write('setState ' + str(STATE['OK']))

t_serial = SerialThread(queue, out_queue)
t_error = RandomErrorThread()

def main():
    # main entry point
    logging.info('started!')
    logging.getLogger().setLevel(logging.DEBUG)

    t_serial.setDaemon(True)
    t_serial.start()

    t_error.setDaemon(True)
    #t_error.start()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    running = True
    while running:
        time.sleep(.05)

if __name__ == "__main__":
    main()