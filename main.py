"""
Garage Door Controller code
Written by Michael Ruppe @ Core Electronics
    - Version 1.0 July 2022

Hosts a static webpage with three garage door control buttons (Up, Stop, Down)
Outputs: Open Drain channels to pull-down garage door controller channels.

Adapted from examples in: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
"""

import time
import network
import uasyncio as asyncio
from machine import Pin

import rp2
import array, time
from leds_modes import rainbow_cycle, wheel, color_chase, pixels_set, pixels_fill, pixels_show
#Leds definitions
NUM_LEDS = 30
PIN_NUM = 0
brightness = 0.5

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

#################################

# Hardware definitions
led = Pin("LED", Pin.OUT, value=1)

data_pin = Pin(20, Pin.OUT, value=0)

# Configure your WiFi SSID and password
ssid = '5G 50% Mocy'
password = 'piotrek2018'

check_interval_sec = 0.25

wlan = network.WLAN(network.STA_IF)


# The following HTML defines the webpage that is served
f = open("page.html","r")
html = f.read()
f.close()

def blink_led(frequency = 0.5, num_blinks = 3):
    for _ in range(num_blinks):
        led.on()
        time.sleep(frequency)
        led.off()
        time.sleep(frequency)

def control_door(cmd):
    if cmd == 'stop':
        pin_stop.on()
        blink_led(0.1, 1)
        pin_stop.off()
        
    if cmd == 'up':
        pin_up.on()
        blink_led(0.1, 1)
        pin_up.off()
    
    if cmd == 'down':
        pin_down.on()
        blink_led(0.1, 1)
        pin_down.off()
        
        
async def connect_to_wifi():
    wlan.active(True)
    wlan.config(pm = 0xa11140)  # Diable powersave mode
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        blink_led(0.1, 10)
        raise RuntimeError('WiFi connection failed')
    else:
        blink_led(0.5, 2)
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

def get_params(request):
    params = request.split('&')
    parameters = []
    for param in params:
        if '=' in param:
            key, value = param.split('=')
            if(value.find(' ')>=0):
                parameters.append(value[0:value.find(' ')])
            else:
                parameters.append(value)
    if len(parameters) == 0 :
        return ['-1','-1','-1']
    return parameters

def change_to_rgb(hex_color):
    clear = hex_color[3:]
    rgb_color = tuple(int(clear[i:i+2], 16) for i in (0, 2, 4))
    return rgb_color

async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass
    
    # find() valid garage-door commands within the request
    request = request_line.decode()
    mode, color, brightness = get_params(request)

    print('mode:',mode)
    print('color:',color)
    print('brightness:',brightness)
    
    rgb_color = change_to_rgb(color)
        
    if mode == "default":
        pixels_fill(rgb_color, ar)
        pixels_show(ar, brightness, NUM_LEDS, sm)
    if mode == "wave":
        print("wave")
        while(True): # add thread
            color_chase(ar, rgb_color, brightness, 0.01, NUM_LEDS, sm)
            if mode != "wave":
                break
    if mode == "rgb":
        print("rgb")
    
    #response = html % stateis
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(html)

    await writer.drain()
    await writer.wait_closed()


async def main():
    print('Connecting to WiFi...')
    asyncio.create_task(connect_to_wifi())

    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))

    while True:
        await asyncio.sleep(check_interval_sec)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()

