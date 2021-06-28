import utime
from machine import Pin, PWM, Timer

# Low-cost multi-channel lighting scene controller - by Stewart Twynham
#
# The aim of this was to create a really simple multi-channel lighting controller
# Most controllers are expensive, use proprietary components and have limited channels.
# The approach here is to use the Raspberry Pi Pico's PWM drivers to switch 12v or 24v leds
#
# Requirements: 1) easily scale to any number of channels
#               2) be able to describe any number of scenes in software
#               3) use soft-dimming
#

# The Led class holds all the properties of led output including the GPIO
# We will use a timer to check where the desired value is different from the actual and change the actual slowly to match
class Led:
    def __init__ (self, gpio, actual = 0, desired = 0):
        self.gpio = Pin(gpio, Pin.OUT) # set up the GPIO pin
        self.pwm = PWM(self.gpio)      # initiate as a PWM output
        self.pwm.freq(10000)           # set the frequency to 10kHz
        self.actual = actual           # this is the actual value of our LED brightness 0..255 
        self.desired = actual          # desired is the value we want 0..255
    
    # turns on the channel immediately to full brightness
    def on (self):
        self.actual = 255
        self.desired = 255
    
    # turns off the channel immediately
    def off (self):
        self.actual = 0
        self.desired = 255

    # we manually create the setter and getter for the desired value because we want to ensure the value is 0..255
    # if desired does not match actual, we will also initialise the updateTimer
    @property
    def desired(self):
        return self.__desired
    
    @desired.setter
    def desired(self, desired):
        if (desired < 0):
            self.__desired = 0
        elif (desired > 255):
            self.__desired = 255
        else:
            self.__desired = desired
            
        if (self.__desired != self.__actual):
            updateTimer.init(freq=75, mode=Timer.PERIODIC, callback=updateChannels)
    
    # when we set the actual value, we check the value is 0..255 and use this value to update the pwm duty cycle
    @property        
    def actual(self):
        return self.__actual
    
    @actual.setter
    def actual(self, actual):
        if (actual < 0):
            self.__actual = 0
        elif (actual > 255):
            self.__actual = 255
        else:
            self.__actual = actual
        self.pwm.duty_u16(self.__actual * self.__actual) # duty cycle is an unsigned 16 bit value so we square it

# set up the GPIO channels using a dict so we can address them with english language keys
channel = {
    "downlighters": Led(10),
    "uplighters": Led(14),
    "accents": Led(17),
    "cabinet": Led(21)    
    }

# the timer runs updateChannels 75 times a second - whenever there is a need to raise or lower led brightness
def updateChannels(timer):
    global channel
    changes = 0               # we check whether we made any changes - if not - we can deinitialise the timer
    
    for led in channel:
        if (channel[led].actual != channel[led].desired):
            if (channel[led].desired > channel[led].actual):        # whenever the brightness needs to be raised, do this faster
                delta = 2
            elif (channel[led].desired == channel[led].actual + 1): # if we are only 1 away, make the delta 1
                delta = 1
            else:
                delta = -1
        
            channel[led].actual += delta
            changes += 1

    if (changes == 0):
        updateTimer.deinit() # if all leds are at the correct brightness, de-initialise the timer

# initialise the timer
# this runs at 75 times a second

updateTimer = Timer()
updateTimer.init(freq=75, mode=Timer.PERIODIC, callback=updateChannels)

# a simple debounce routine which waits for the button to be pressed

def waitfor(button):
    while (button.value() == 1): # if the button is down - wait a short time to debounce
        utime.sleep(0.2)
    while (button.value() == 0): # now wait for the button to be pressed
        pass

# we will use a single button in this example - to switch between our 'scenes'
button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)


# we now have the main loop - where we define our scenes -
# we only have four outputs in this example, but we can add as many output channels
# as we have available GPIO ports, and an unlimited number of scenes 

while(1):
    print ("ON")
    channel["downlighters"].desired = 255
    channel["accents"].on()
    channel["uplighters"].desired = 255
    channel["cabinet"].desired = 255
    waitfor(button)
    
    print ("Dim")
    channel["downlighters"].desired = 128
    channel["cabinet"].desired = 128
    waitfor(button)
    
    print ("TV")
    channel["downlighters"].desired = 16
    channel["accents"].desired = 64
    channel["uplighters"].desired = 16
    channel["cabinet"].desired = 16
    waitfor(button)
    
    print ("Bar")
    channel["uplighters"].desired = 64
    channel["downlighters"].desired = 64
    channel["accents"].desired = 255
    waitfor(button)   
    


