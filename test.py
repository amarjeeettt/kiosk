import datetime

# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the datetime object into a string without seconds
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

# Print the formatted datetime
print("Formatted datetime without seconds:", formatted_datetime)
