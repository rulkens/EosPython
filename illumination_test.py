from lib.api.EOS_API import EOS_API
import socket
import sys
import time
import csv
import datetime

# decimal range generator
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

# connect to an Android server on my phone
server_address = ('192.168.1.68', 8080)

def ask_illuminance():
    """communicate with a custom TCP socket on my Galaxy S4 to measure illuminance levels"""
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    data = -1
    try:
            more = True
            data = sock.recv(40)
    finally:
        sock.close()
        return float(data) # some error response

def test1():
    """Test 1: range of lights, sweep"""
    test_nr = 1
    range_start = 5
    range_end = 20
    file_add = '%s-%s' % (range_start, range_end)
    file_date = datetime.datetime.now().strftime("%Y%m%d_%H.%M")
    file_name = "test/data/illu-%s-%s-%s.csv" % (test_nr, file_date, file_add)
    # CSV file to save to
    out = csv.writer(open(file_name,"w"), delimiter=',',quoting=csv.QUOTE_MINIMAL)

    # some user feedback
    print "Running EOS sweep test from light %s to %s" % (range_start, range_end-1)
    print "Saving to filename %s" % file_name

    # loop through the specified lights in the range and sweep the intensity from 0.0 to 1.0 for each one
    for light_index in range(range_start,range_end):
        data_item = [light_index]
        print 'writing row %s' % light_index

        # extra waiting time to make sure all lights are off
        time.sleep(3)
        # sweep through the entire intensity range of one light
        for i in drange(0, 1.02, 0.02):
            EOS_API('only', [light_index, i])
            # wait a bit, allow the light to turn on
            # TODO: make sure we allow the light enough time to get to the right itensity
            time.sleep(0.6)
            # ask for the current illuminance
            ill = ask_illuminance()
            # print it
            result = [round(i,3), ill]
            print result
            data_item.append(ill)

        # save data to file
        out.writerow(data_item)

def test2():
    test_nr = 2
    range_start = 0.2
    range_end = 0.8
    range_step = 0.01
    file_add = '%s-%s' % (range_start, range_end)
    file_date = datetime.datetime.now().strftime("%Y%m%d_%H.%M")
    file_name = "test/data/illu-%s-%s-%s.csv" % (test_nr, file_date, file_add)
    # CSV file to save to
    out = csv.writer(open(file_name,"w"), delimiter=',',quoting=csv.QUOTE_MINIMAL)

    # some user feedback
    print "Running EOS light test from light %s to %s" % (range_start, range_end)
    print "Saving to filename %s" % file_name

    data_item = []
    for light_pos in drange(range_start,range_end, range_step):
        print 'writing row %s' % light_pos
        EOS_API('light', [light_pos, 1.5, 1.0, 'linear'])
        time.sleep(1)
        ill = ask_illuminance()
        data_item.append(ill)
    # save data to file
    out.writerow(data_item)

test2()