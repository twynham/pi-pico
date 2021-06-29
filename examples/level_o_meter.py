import utime
import random
import picoexplorer as display
from machine import Pin, ADC, Timer

# Level-o-meter
# By Stewart Twynham
#
# Display an animated level counter on the display with six LEDs run as a bargraph
#

width = display.get_width()
height = display.get_height()
centre = round(width / 2)
middle = round(height / 2)

display_buffer = bytearray(width * height * 2)  # 2-bytes per pixel (RGB565)
display.init(display_buffer)

# initialise the colours

class Colour:
    def __init__(self, bk, bb, fl, tx):
        self.background = bk
        self.bubble = bb
        self.fill = fl
        self.text = tx

Colours = []

# red
Colours.append(
    Colour(
        display.create_pen(128,64,64), display.create_pen(255,128,128), display.create_pen(128,64,64), display.create_pen(255,0,0)
        )
    )

# blue
Colours.append(
    Colour(
        display.create_pen(64,64,128), display.create_pen(128,128,255), display.create_pen(64,64,128), display.create_pen(255,255,255)
        )
    )


# initialise our LED bargraph
bartimer = Timer()
leds = []
for i in range (0,6):
    leds.append(Pin(i + 1, Pin.OUT))

def update_bargraph(reading):
    for i in range (0,6):
        if (reading > i):
            leds[5-i].value(1)
        else:
            leds[5-i].value(0)

def update_leds(bartimer):
    if (bargraph_value == 0):
        for i in range (0,5):
            leds[i].value(0)
        leds[5].toggle()
    else:
        for i in range (0,6):
            if (bargraph_value > i):
                leds[5-i].value(1)
            else:
                leds[5-i].value(0)

def scale(reading, max_value):
    return (round((reading - 250) / 65285 * max_value))

class Bubble:
    def __init__(self, x, y, r, t):
        self.xpos = x
        self.ypos = y
        self.radius = r
        self.age = t


pot = ADC(1).read_u16()
bargraph_value = scale(pot, 6)
bartimer.init(freq=2.5, mode=Timer.PERIODIC, callback=update_leds)

# initialise bubbles
Bubbles = []
for i in range(0, 25):
    r = random.randint(0, (3 + scale(pot, 10))) + 3
    Bubbles.append(
        Bubble(
            random.randint(r, r + (width - 2 * r)),
            random.randint(r, r + (height - 60 - 1 * r)) + 60,
            r,
            0
        )
    )

while True:

    this_colour = 1
    pot = ADC(1).read_u16()
    litres = scale(pot, 500)
    percentage = scale(pot, 100)
    bargraph_value = scale(pot, 6)
    
    if (bargraph_value < 2):
        this_colour = 0
    
    level = scale(pot, height-60)
    max_bubbles = scale(pot, 30)
    
    display.set_pen(40, 40, 40)
    display.clear()
    
    display.set_pen(Colours[this_colour].bubble)
    display.rectangle(0,height - level - 2,width,2)
    display.set_pen(Colours[this_colour].background)
    display.rectangle(0,height - level,width,level)
    
    display.set_pen(Colours[this_colour].text)
    display.text ("Fresh water", 4, 4, 236, 2)
    display.text ("{:} l".format(litres), 4, 24, 236, 4)
    display.text ("{:.0f}%".format(percentage), 126, 18, 236, 5)

    count = 0
    for bubble in Bubbles:
        bubble.ypos -= (0.07 * bubble.age * bubble.age)
        ymin = bubble.radius + height - level
        bubble.age += 1
        count += 1

        if bubble.ypos < ymin:
            r = random.randint(0, (3 + scale(pot, 10))) + 3
            bubble.radius = r
            bubble.ypos = height - bubble.radius
            bubble.xpos = random.randint(r, r + (height - 1 * r))
            bubble.age = random.randint(0,4)
        
        #display.set_pen(bubble.colour)
        if (bubble.radius < level and count < max_bubbles):
            display.set_pen(Colours[this_colour].bubble)
            display.circle(int(bubble.xpos), int(bubble.ypos), int(bubble.radius))
            display.set_pen(Colours[this_colour].fill)        
            display.circle(int(bubble.xpos), int(bubble.ypos), int(bubble.radius)-2)
    
    
    # show warning message if very low
    if (bargraph_value < 2):
        display.set_pen(Colours[this_colour].text)
        display.rectangle(centre-80,middle - 40,160,80)
        display.set_pen(Colours[this_colour].background)
        display.text ("Level very low", centre-70, middle-30, 140, 3)        
        
        
    display.update()
    
    utime.sleep(0.01)