import time
from gpiozero import Button

coinslot = Button(10)

while True:
    coinslotState = True
    counter = 0
    while coinslotState:
            if coinslot.is_pressed:
                counter+=1
                time.sleep(.05)
                print(counter)
