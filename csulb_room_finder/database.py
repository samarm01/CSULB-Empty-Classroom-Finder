import sqlite3

DATABASE_FILE = "schedule.db"

def setup_database():
    """
    Creates the database file and the 'classes' table if they don't already exist.
    """
    # conn will be our connection to the database
    # The 'with' statement ensures the connection is closed automatically
    with sqlite3.connect(DATABASE_FILE) as conn:
        # cursor is used to execute SQL commands
        cursor = conn.cursor()
        
        # Execute the SQL command to create the table.
        # "IF NOT EXISTS" prevents an error if the table already exists.
        # TEXT, INTEGER are the data types for the columns.
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
        # Commit the changes to the database
        conn.commit()
        print("Database setup complete. Table 'classes' is ready.")

def save_classes_to_db(class_list):
    """
    Saves a list of scraped class data to the database.
    This function first clears the old data before inserting the new data.

    Args:
        class_list (list): A list of class dictionaries from the scraper.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        
        # Step 1: Clear all existing data from the table to ensure freshness
        cursor.execute("DELETE FROM classes")
        print(f"Cleared old data from the 'classes' table.")
        
        # Step 2: Iterate through the scraped data and insert it
        classes_to_insert = []
        for class_info in class_list:
            # IMPORTANT: A class on 'MWF' becomes three separate database entries.
            # This makes searching by a single day (e.g., 'M') much easier.
            for day in class_info['days']:
                classes_to_insert.append((
                    class_info['course_title'],
                    day,
                    class_info['start_time'],
                    class_info['end_time'],
                    class_info['building'],
                    class_info['room'],
                    class_info['instructor']
                ))

        # Use executemany for a fast bulk insert
        cursor.executemany("""
            INSERT INTO classes (course_title, day, start_time, end_time, building, room, instructor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, classes_to_insert)
        
        conn.commit()
        print(f"Successfully saved {len(classes_to_insert)} class bookings to the database.")

def find_empty_rooms(day, start_time, end_time):
    """
    Finds all rooms that are not occupied during a specific time slot on a given day.

    Args:
        day (str): The day to check (e.g., 'M', 'Tu', 'W').
        start_time (int): The start of the time slot in 24-hour format (e.g., 1300).
        end_time (int): The end of the time slot in 24-hour format (e.g., 1400).

    Returns:
        list: A sorted list of available rooms as strings (e.g., ['CBA-123', 'PH1-210']).
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        
        # Step 1: Get a set of ALL unique rooms from the database
        cursor.execute("SELECT DISTINCT building, room FROM classes")
        all_rooms = {f"{building}-{room}" for building, room in cursor.fetchall()}

        # Step 2: Get a set of all rooms that are OCCUPIED during the requested time slot.
        # The logic for an overlap is:
        # (class_start_time < user_end_time) AND (class_end_time > user_start_time)
        cursor.execute("""
            SELECT DISTINCT building, room FROM classes
            WHERE day = ? AND start_time < ? AND end_time > ?
        """, (day, end_time, start_time))
        
        occupied_rooms = {f"{building}-{room}" for building, room in cursor.fetchall()}
        
        # Step 3: The empty rooms are the ones in all_rooms but not in occupied_rooms
        empty_rooms = sorted(list(all_rooms - occupied_rooms))
        
        print(f"Found {len(empty_rooms)} empty rooms for the selected slot.")
        return empty_rooms
        
# --- Testing Block ---
# This code runs only when you execute `python database.py` directly.
# It allows us to test the database functions in isolation.
if __name__ == "__main__":
    print("--- Testing Database Functions ---")

    # Create some fake data that mimics our scraper's output
    sample_classes = [
        {'course_title': 'TEST 101', 'days': ['M', 'W'], 'start_time': 1000, 'end_time': 1100, 'building': 'CBA', 'room': '101', 'instructor': 'Smith A'},
        {'course_title': 'TEST 102', 'days': ['M'], 'start_time': 1130, 'end_time': 1230, 'building': 'CBA', 'room': '101', 'instructor': 'Jones B'},
        {'course_title': 'TEST 201', 'days': ['Tu'], 'start_time': 1000, 'end_time': 1100, 'building': 'PH1', 'room': '205', 'instructor': 'Doe C'}
    ]

    # 1. Set up the database
    setup_database()
    
    # 2. Save our sample data
    save_classes_to_db(sample_classes)
    
    # 3. Test the search function
    print("\n--- Searching for empty rooms on Monday from 10:30 AM to 11:30 AM ---")
    # Expected: CBA-101 is busy from 10:00-11:00, so it's occupied.
    # PH1-205 should be empty.
    empty_rooms_test1 = find_empty_rooms('M', 1030, 1130)
    print("Results:", empty_rooms_test1)
    
    print("\n--- Searching for empty rooms on Monday from 1:00 PM to 2:00 PM ---")
    # Expected: Both rooms should be free.
    empty_rooms_test2 = find_empty_rooms('M', 1300, 1400)
    print("Results:", empty_rooms_test2)