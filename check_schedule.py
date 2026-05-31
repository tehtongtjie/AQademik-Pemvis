# import sqlite3

# conn = sqlite3.connect("database/akademiq.db")
# cursor = conn.cursor()

# cursor.execute("SELECT * FROM schedules")
# print("Schedules in database:")
# for row in cursor.fetchall():
#     print(f"  {row}")

# conn.close()

import sqlite3

conn = sqlite3.connect("database/akademiq.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT OR IGNORE INTO schedules (day_of_week, course_name, lecturer, start_time, end_time, room, color)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('Selasa', 'Basis Data', 'Dr. Siti Aminah, M.Kom.', '08:00', '10:30', 'Ruang 202', '#2ecc71'))

cursor.execute("""
    INSERT OR IGNORE INTO schedules (day_of_week, course_name, lecturer, start_time, end_time, room, color)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('Kamis', 'Basis Data', 'Dr. Siti Aminah, M.Kom.', '13:00', '15:30', 'Lab B201', '#2ecc71'))

conn.commit()
print("Schedule added for Basis Data")

cursor.execute("SELECT * FROM schedules WHERE course_name = 'Basis Data'")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()