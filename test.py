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
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    print("Program terminated by user")
