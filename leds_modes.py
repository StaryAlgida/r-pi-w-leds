import array
import time


def rainbow_cycle(wait, NUM_LEDS):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)
        

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def color_chase(ar, color, brightness, wait, NUM_LEDS, sm):
    for i in range(NUM_LEDS):
        pixels_set(i, color, ar)
        time.sleep(wait)
        pixels_show(ar, brightness, NUM_LEDS, sm )
    for i in range(NUM_LEDS):
        pixels_set(i, (0,0,0), ar)
        time.sleep(wait)
        pixels_show(ar, brightness, NUM_LEDS, sm )

def pixels_show(ar, brightness, NUM_LEDS, sm):
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * float(brightness))
        g = int(((c >> 16) & 0xFF) * float(brightness))
        b = int((c & 0xFF) * float(brightness))
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)

def pixels_set(i, color, ar):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color, ar):
    for i in range(len(ar)):
        pixels_set(i, color, ar)

