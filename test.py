import time
from gpiozero import Button
import cups

coinslot = Button(22)

# Connect to the local CUPS server
conn = cups.Connection()

# Get a list of available printers
printers = conn.getPrinters()

# Get the first printer in the list
printer_name = list(printers.keys())[0]

# Specify the file you want to print
file_path = "HATDOG.pdf"  # Change this to the path of your document file

# Wait for the button to be pressed before starting
while not coinslot.is_pressed:
    pass

# Button is pressed, start counting coins
counter = 0
while True:
    if coinslot.is_pressed:
        counter += 1
        time.sleep(0.05)
        print(counter)
        
        # Check if the counter is equal to 10
        if counter == 10:
            # Print the file
            job_id = conn.printFile(printer_name, file_path, "Print Job", {})
            print("Print job submitted with ID:", job_id)
            counter = 0  # Reset counter after printing