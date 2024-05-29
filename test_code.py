import sqlite3

with sqlite3.connect("./database/kiosk.db") as conn_sqlite:
    cursor = conn_sqlite.cursor()
    cursor.execute(
        "UPDATE kiosk_settings SET bondpaper_quantity = ?, ink_level = ?, coins_left = 0",
        (
            100,
            1500,
        ),
    )
