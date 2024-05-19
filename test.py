"""
import time
from gpiozero import Button

coinslot = Button(22)

while True:
    coinslotState = True
    counter = 0
    while coinslotState:
            if coinslot.is_pressed:
                counter+=1
                time.sleep(.05)
                print(counter)
"""

import os
import glob

def delete_process_file(form_name):
    # Find files matching the pattern
    process_files = glob.glob(f"./img/process/{form_name}-*.jpg")
    
    if not process_files:
        print("No file found to delete.")
        return
    
    # Loop through the matched files and delete each one
    for file_path in process_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} deleted successfully.")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")

# Example usage
delete_process_file("test")
