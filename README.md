# EosPython
Python REST, TCP, UDP and websocket I2C Raspberry Pi interface with [AdaFruit PWM Driver](http://www.adafruit.com/products/815).

## HTTP Server
EosPython comes with a simple webserver, both with an REST API and websocket interface. It includes an admin interface 
that communicates with the server using [SockJS](http://sockjs.org).

You have to have the following pip packages installed:

    tornado
    sockjs-tornado

Also, you need node with bower to install the frontend dependencies. When you have bower installed, run `bower install`
to install the dependencies into `public/vendor`

The server port defaults to `5153` and can be configured using the following environment variable:

    EOS_SOCKET_PORT=5153
    
To run the server on your Raspberry PI, navigate to the main directory and

    sudo wsd

You can then navigate to the web interface on the pre-defined port or write your own websocket interface!

## TCP Server
For faster communication directly with the api you can run the TCP server. By default it starts on port 5154. The TCP server
provides a direct interface to the EOS API with JSON-based messages.

To start it, run:

    sudo tcpd
    
## UDP Server

When you want fast, real-time communication with EOS, you should use the UDP server. It allows for sending binary messages,
but it only has functionality for updating all the halogens and the leds at once. You will have to write your own 
higher-level API for it. An implementation in Javascript can be found in the [EosNode](https://github.com/rulkens/EosNode).

Run the server:

    sudo udpd

## Eos Hardware
The EOS lamp contains 32 10W, 12V halogen lights. All of them can be switched by applying a 5V voltage to their 
associated MOSFET. The connector is plugged into a circuit that pulls down the voltage down to ground by default, 
with a 10kOhm resistor. This circuit is connected to two Adafruit PWM drivers that supply the PWM signals to all the 
lights.

The PWM drivers are connected to a [Raspberry Pi 2 Model B](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/) 
on the [I2C bus](http://en.wikipedia.org/wiki/I%C2%B2C), using [GPIO pins](http://pi.gadgetoid.com/pinout)
2,3,5,7 and 9. Normally we would use pin 1 for 3.3v power, but since the MOSFETs don't switch with 3.3V we need to use
5V. The Adafruit PWM drivers have no problem running on 5V power.

To get the PWM drivers to work, I followed the excellent 
[Adafruit I2C tutorial](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/overview). You need to
install a couple of packages before you can get started:

    sudo apt-get install python-dev
    sudo apt-get install python-rpi.gpio
    
Then to install I2C support for python

    sudo apt-get install python-smbus
    sudo apt-get install i2c-tools
    
Install the kernel support for I2C using `raspbian-config`

    sudo raspi-config
 
 
The PWM drivers use the bus numbers `0x40` and `0x41`. You can check if the drivers are connected properly by running:

    sudo i2cdetect -y 1
    
or
    
    sudo ./testi2c.sh
    
You should see something like this:

         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- --
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    40: 40 41 -- -- -- -- -- -- -- -- -- -- -- -- -- --
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    70: 70 -- -- -- -- -- -- --

### I2C speed

By default, the Raspberry Pi i2c module runs at 100KHz. Sending the PWM values to the drivers with this speed takes about
24ms. This equals to a framerate of about 42 fps, which is quite slow. By increasing the baudrate for i2c and improving
the code for sending values (only update the off bytes of the PWM signal) one update cycle runs in about 8-10ms. This can
support a framerate of around 100-120fps.

Setting the I2C framerate is done in the `/boot/settings.txt` file. Add this line to the end:

    dtparam=i2c1_baudrate=400000

This sets the baudrate to 400KHz. Then reboot!

    sudo reboot
    


## Foot interface

On the bottom of the lamp you will see a circular LED strip that can be used to control the lights directly on the lamp.
It uses an Arduino that is connected with a serial interface to the Raspberry Pi and has it's own protocol for sending
and receiving messages.

The LED ring is a 12-LED Neopixel ring that is controlled with the Arduino Duemilenova. The sketch can be found in the
`arduino` folder. To make sure you can communicate with the Arduino, install the Arduino and PySerial library:

    sudo apt-get install arduino
    sudo apt-get install python-serial

## Auto-starting servers

By default, all three servers are started as daemons when the Raspberry Pi is turned on. This is done with a default 
Linux subsystem, i.e. a file in `/etc/init.d/`. The files for this can be found in the `init.d/` folder. To install, copy
them to the `/etc/init.d` directory:

    sudo cp init.d/eoswsd /etc/init.d
    sudo cp init.d/eostcpd /etc/init.d
    sudo cp init.d/eosudpd /etc/init.d
    
Then add them to the default run level, so they get started at boot.

    sudo update-rc.d eosudpd defaults
    sudo update-rc.d eoswsd defaults
    sudo update-rc.d eostcpd defaults

You can also manually start, stop and restart a server:

    sudo /etc/init.d/eoswsd start
    sudo /etc/init.d/eoswsd stop
    sudo /etc/init.d/eoswsd restart

## API
The API is implemented in the `lib/api/EOS_API.py` file. It exposes a single function, called EOS_API and is used by
the command line tool and the socket server. Generally, it works by providing it with an action and optional
arguments. The following actions are available:

    on(index=None)                              - turns all lights on
    off(index=None)                             - turns all lights off
    one(index=0, intensity=1.0)                 - turn one light on to a specific intensity (0-1)
    set(intensities)                            - supply a list of intensities (0-1)
    all(intensity)                              - set all lights to the specified intensity (0-1)
    only(index, intensity)                      - turn one light on with the specified intensity(0-1) and all other lights off
    
    status                                      - get the status of the lights as a list of intensity values
    setFreq(freq=500)
    gamma(value=1.0)

    light(pos=0.0, size=0.1, intensity=1.0)     - 
    glow(action)                                - action can be `on` or `off`
    
### Turning lights on and off
With the API it's very easy to turn all or individual lights on or off. Let's use the command line tool to turn all
lights on, then off.

    sudo ./eos on
    sudo ./eos off
    
### Set the intensity of a specific light
The driver can set the intensity of all lights with an accuracy of 4096 steps, a bit less when using gamma. In the
API interface, a value of `0-1` is mapped to a PWM value and sent to the driver. 

To turn light 23 on to half intensity, use:

    sudo ./eos one 23 0.5
    
### Set all lights at once

When you run the following command you will notice that the lights are flickering a little bit. The poor power
supply has problems with the intense variation in current that 32 PWM signals are causing.

    sudo ./eos all 0.5
    
When writing higher-level programs for the EOS you have to take care that you only use a couple of lamps at once, 
or get a power supply with more juice (I use a 400W customized PC power supply).

### Create a light at the bottom
The EOS API also has some higher-level functionality. One of those is to create a light spanning multiple lamps.
It gives a very nice effect, especially when you move the light. Run the following command

    sudo ./eos light 0 4 1 'cube'
    
This creates a light with `position = 0` (at the bottom), with `size = 4` and `intensity = 1`. This is a nice light 
for a quiet night, listening to music and enjoying a good glass of whine.


## Background
The EOS lamp was my graduation project at the faculty of Industrial Design at the Eindhoven University of Technology.
It was initially also equipped with a grid of sensor wires, so people could use their hands to control the light. 
In its current state it can be controlled by anyone who knows the server address :) using an online interface.

## Future
Do you have any ideas what you would like to do with the EOS lamp? Then drop me a line and we can see what projects we
can initiate!
