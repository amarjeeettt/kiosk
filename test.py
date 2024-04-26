import time
from gpiozero import Button

def coin_inserted():
    global counter
    counter += 1
    print("Coin inserted. Total coins:", counter)

coinslot = Button(17)
coinslot.when_pressed = coin_inserted

counter = 0
try:
    while True:
        time.sleep(0.05)  # Keep the program running
except KeyboardInterrupt:
    print("Program terminated by user")



"""
import RPi.GPIO as GPIO
import time

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Pin number to reset
pin_number = 17

# Set pin as input and pull it low (reset)
GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Wait for a short duration
time.sleep(0.1)

# Set pin back to output mode and pull it low (if necessary)
GPIO.setup(pin_number, GPIO.OUT, initial=GPIO.LOW)

# Clean up GPIO
GPIO.cleanup()
"""
