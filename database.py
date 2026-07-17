import sqlite3

DATABASE_FILE = "schedule.db"

def setup_database():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_title TEXT NOT NULL,
                day TEXT NOT NULL,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                building TEXT NOT NULL,
                room TEXT NOT NULL,
                instructor TEXT
            )
        """)
        conn.commit()
    print("Database setup complete.")

def save_classes_to_db(class_list):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM classes")
        classes_to_insert = []
        for class_info in class_list:
            for day in class_info['days']:
                classes_to_insert.append((
                    class_info['course_title'], day, class_info['start_time'],
                    class_info['end_time'], class_info['building'], class_info['room'],
                    class_info['instructor']
                ))
        cursor.executemany("""
            INSERT INTO classes (course_title, day, start_time, end_time, building, room, instructor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, classes_to_insert)
        conn.commit()
        print(f"Saved {len(classes_to_insert)} bookings.")

def get_all_buildings():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT building FROM classes ORDER BY building")
        buildings = [item[0] for item in cursor.fetchall()]
        return buildings

def find_empty_rooms(day, start_time, end_time, building_filter=None):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        all_rooms_query = "SELECT DISTINCT building, room FROM classes"
        if building_filter:
            all_rooms_query += " WHERE building = ?"
            cursor.execute(all_rooms_query, (building_filter,))
        else:
            cursor.execute(all_rooms_query)
        all_rooms = {f"{b}-{r}" for b, r in cursor.fetchall()}

        occupied_rooms_query = "SELECT DISTINCT building, room FROM classes WHERE day = ? AND start_time < ? AND end_time > ?"
        params = [day, end_time, start_time]
        if building_filter:
            occupied_rooms_query += " AND building = ?"
            params.append(building_filter)
        
        cursor.execute(occupied_rooms_query, tuple(params))
        occupied_rooms = {f"{b}-{r}" for b, r in cursor.fetchall()}
        
        empty_rooms = sorted(list(all_rooms - occupied_rooms))
        print(f"Found {len(empty_rooms)} empty rooms.")
        return empty_rooms

# --- NEW FUNCTION FOR PHASE 6 ---
def find_room_schedule(day, start_time, end_time, classroom):
    """
    Finds all classes scheduled in a specific room that overlap with a given time slot.

    Args:
        day (str): The day to check (e.g., 'M').
        start_time (int): The start of the time slot (e.g., 1300).
        end_time (int): The end of the time slot (e.g., 1400).
        classroom (str): The classroom to check (e.g., 'CBA-123').

    Returns:
        list: A list of dictionaries, each containing info about an occupying class.
              Returns an empty list if the room is free.
    """
    try:
        building, room = classroom.split('-', 1)
    except ValueError:
        # Handle cases where the input format is wrong
        return []

    with sqlite3.connect(DATABASE_FILE) as conn:
        # Use row_factory to get results as dictionaries instead of tuples
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # Query for any classes in that specific room/day that overlap with the time
        cursor.execute("""
            SELECT course_title, instructor, start_time, end_time FROM classes
            WHERE day = ? AND building = ? AND room = ? AND start_time < ? AND end_time > ?
        """, (day, building.strip(), room.strip(), end_time, start_time))
        
        # Convert the sqlite3.Row objects into regular dictionaries
        schedule = [dict(row) for row in cursor.fetchall()]
        return schedule