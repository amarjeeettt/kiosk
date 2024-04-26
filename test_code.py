import cups

def get_first_printer_info():
    conn = cups.Connection()
    printers = conn.getPrinters()
    if printers:
        first_printer_name = list(printers.keys())[0]
        printer_info = conn.getPrinterAttributes(first_printer_name)
        return first_printer_name, printer_info
    else:
        return None, None

def get_ink_level(printer_info):
    ink_level = printer_info.get('printer-state-message', "Unknown")
    return ink_level

def main():
    printer_name, printer_info = get_first_printer_info()
    if printer_name and printer_info:
        ink_level = get_ink_level(printer_info)
        print(f"Ink Level for {printer_name}: {ink_level}")
    else:
        print("No printers found.")

if __name__ == "__main__":
    main()
