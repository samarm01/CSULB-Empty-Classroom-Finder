import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from datetime import datetime

# Import the functions from your other files
import scraper
import database

class RoomFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSULB Room Finder")
        self.root.geometry("500x600")

        # --- UI Elements ---
        self.update_frame = ttk.Frame(root, padding="10")
        self.update_button = ttk.Button(self.update_frame, text="Update Class Data", command=self.start_update_thread)
        self.last_updated_label = ttk.Label(self.update_frame, text="Last Updated: Never")

        self.search_frame = ttk.LabelFrame(root, text="Find an Empty Room", padding="10")
        
        self.day_label = ttk.Label(self.search_frame, text="Day:")
        self.day_var = tk.StringVar()
        self.day_dropdown = ttk.Combobox(self.search_frame, textvariable=self.day_var, values=["M", "Tu", "W", "Th", "F", "Sa", "Su"], state="readonly")
        self.day_dropdown.set("M")

        self.start_time_label = ttk.Label(self.search_frame, text="Start Time (e.g., 1300):")
        self.start_time_entry = ttk.Entry(self.search_frame)
        self.end_time_label = ttk.Label(self.search_frame, text="End Time (e.g., 1430):")
        self.end_time_entry = ttk.Entry(self.search_frame)

        # --- New Building Filter ---
        self.building_label = ttk.Label(self.search_frame, text="Building (Optional):")
        self.building_var = tk.StringVar()
        self.building_dropdown = ttk.Combobox(self.search_frame, textvariable=self.building_var, state="readonly")
        self.building_dropdown.set("All Buildings")

        self.find_button = ttk.Button(self.search_frame, text="Find Available Rooms", command=self.handle_find)

        self.results_frame = ttk.LabelFrame(root, text="Results", padding="10")
        self.results_listbox = tk.Listbox(self.results_frame)
        self.results_scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.config(yscrollcommand=self.results_scrollbar.set)
        
        self.status_label = ttk.Label(root, text="Ready", padding="5", relief=tk.SUNKEN)

        # --- Layout ---
        self.update_frame.pack(fill=tk.X, padx=10, pady=5)
        self.update_button.pack(side=tk.LEFT)
        self.last_updated_label.pack(side=tk.RIGHT)

        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        self.search_frame.columnconfigure(1, weight=1)
        self.day_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.day_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.start_time_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.end_time_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.building_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.building_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        self.find_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # --- Initial Application Setup ---
        self.initialize_app()

    def initialize_app(self):
        """Sets up the database and loads initial data into the UI on startup."""
        database.setup_database()
        self.update_building_dropdown()
        self.update_timestamp()

    def update_timestamp(self):
        """Updates the 'Last Updated' label with the database file's modification time."""
        if os.path.exists(database.DATABASE_FILE):
            mod_time = os.path.getmtime(database.DATABASE_FILE)
            dt_object = datetime.fromtimestamp(mod_time)
            self.last_updated_label.config(text=f"Last Updated: {dt_object.strftime('%Y-%m-%d %H:%M:%S')}")

    def update_building_dropdown(self):
        """Fetches building list from DB and populates the dropdown."""
        buildings = database.get_all_buildings()
        self.building_dropdown['values'] = ["All Buildings"] + buildings
        self.building_var.set("All Buildings") # Reset selection

    def start_update_thread(self):
        """Starts the scraping process in a new thread to keep the UI responsive."""
        self.update_button.config(state=tk.DISABLED)
        self.find_button.config(state=tk.DISABLED)
        self.status_label.config(text="Updating data... This may take a minute.")
        # Create and start the thread
        thread = threading.Thread(target=self.handle_update)
        thread.start()

    def handle_update(self):
        """The actual scraping and database saving logic."""
        all_classes = scraper.get_all_class_schedules()
        if all_classes:
            database.save_classes_to_db(all_classes)
            # When done, schedule UI updates to run on the main thread
            self.root.after(0, self.on_update_complete)
        else:
            self.root.after(0, self.on_update_failed)

    def on_update_complete(self):
        """UI updates to perform after a successful scrape."""
        self.status_label.config(text="Update complete. Ready.")
        self.update_timestamp()
        self.update_building_dropdown()
        self.update_button.config(state=tk.NORMAL)
        self.find_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "Class data has been updated successfully.")

    def on_update_failed(self):
        """UI updates to perform after a failed scrape."""
        self.status_label.config(text="Update failed. Please check connection.")
        self.update_button.config(state=tk.NORMAL)
        self.find_button.config(state=tk.NORMAL)
        messagebox.showerror("Error", "Failed to scrape class data. Please check your internet connection and try again.")
        
    def handle_find(self):
        """Handles the logic for the 'Find Available Rooms' button."""
        day = self.day_var.get()
        start_time_str = self.start_time_entry.get()
        end_time_str = self.end_time_entry.get()
        building = self.building_var.get()

        # --- Input Validation ---
        try:
            start_time = int(start_time_str)
            end_time = int(end_time_str)
            if start_time >= end_time:
                messagebox.showerror("Input Error", "Start time must be before end time.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for start and end times (e.g., 1300).")
            return
        
        # --- Perform Search ---
        building_filter = None if building == "All Buildings" else building
        empty_rooms = database.find_empty_rooms(day, start_time, end_time, building_filter)
        
        # --- Display Results ---
        self.results_listbox.delete(0, tk.END) # Clear previous results
        if not empty_rooms:
            self.results_listbox.insert(tk.END, "No empty rooms found for this time slot.")
        else:
            for room in empty_rooms:
                self.results_listbox.insert(tk.END, room)

# --- Main Program Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = RoomFinderApp(root)
    root.mainloop()