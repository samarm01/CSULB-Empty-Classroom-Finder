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

# --- NEW FUNCTION ---
def get_all_buildings():
    """Gets a sorted list of all unique building names from the database."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT building FROM classes ORDER BY building")
        # fetchall returns a list of tuples, so we extract the first item of each tuple
        buildings = [item[0] for item in cursor.fetchall()]
        return buildings

# --- MODIFIED FUNCTION ---
def find_empty_rooms(day, start_time, end_time, building_filter=None):
    """
    Finds empty rooms, now with an optional filter for a specific building.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()

        # Base query to get all rooms
        all_rooms_query = "SELECT DISTINCT building, room FROM classes"
        if building_filter:
            all_rooms_query += " WHERE building = ?"
            params = (building_filter,)
            cursor.execute(all_rooms_query, params)
        else:
            cursor.execute(all_rooms_query)
        all_rooms = {f"{b}-{r}" for b, r in cursor.fetchall()}

        # Query to get occupied rooms
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