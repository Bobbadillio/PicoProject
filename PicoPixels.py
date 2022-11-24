from neopixel import NeoPixel
from utime import sleep
import math

NEOPIXEL_PIN = 0
NUMBER_PIXELS = 256

GROUP_CYCLES = 100
GROUP_INDEX = 0

strip = NeoPixel(machine.Pin(NEOPIXEL_PIN), NUMBER_PIXELS)

for each_index in range(256):
    r_index = each_index
    g_index = (NUMBER_PIXELS-each_index)%NUMBER_PIXELS
    strip[each_index] = (r_index, g_index,127)
    #strip[each_index] = (0, g_index,0)
    #strip[each_index] = (r_index, 0,0)

strip.write()
sleep(.5)
    
while True:
    # TODO: better comment
    for each_index in range(256):
        r_index = each_index
        g_index = each_index
        b_value = 127+math.ceil(127*math.cos(2*math.pi*((each_index+GROUP_INDEX)%NUMBER_PIXELS)/NUMBER_PIXELS))
        strip[each_index] = (
            (strip[r_index][0]+1)%256,
            (strip[g_index][1]+1)%256,
            b_value
        )
        #strip[each_index] = (0,0,b_value)
        #strip[each_index] = ((strip[r_index][0]+1)%256, 0,0)
        #strip[each_index] = (0, (strip[g_index][1]+1)%256,0)
    
    GROUP_INDEX = (GROUP_INDEX+1)%NUMBER_PIXELS
    strip.write()
    sleep(.00005)
