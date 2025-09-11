import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from datetime import datetime
import queue

import scraper
import database

class RoomFinderApp:
    DAY_MAP = { "Monday": "M", "Tuesday": "Tu", "Wednesday": "W", "Thursday": "Th", "Friday": "F", "Saturday": "Sa", "Sunday": "Su" }

    def __init__(self, root):
        self.root = root
        self.root.title("CSULB Room Finder")
        self.root.geometry("500x800") # Increased height for disclaimer

        self.progress_queue = queue.Queue()
        self.scraping_in_progress = False

        # --- UI Elements ---
        self.update_frame = ttk.Frame(root, padding="10")
        self.update_button = ttk.Button(self.update_frame, text="Update Class Data", command=self.start_update_thread)
        self.last_updated_label = ttk.Label(self.update_frame, text="Last Updated: Never")
        
        self.search_frame = ttk.LabelFrame(root, text="Find an Empty Room", padding="10")
        self.day_label = ttk.Label(self.search_frame, text="Day:")
        self.day_var = tk.StringVar()
        self.day_dropdown = ttk.Combobox(self.search_frame, textvariable=self.day_var, values=list(self.DAY_MAP.keys()), state="readonly")
        self.day_dropdown.set("Monday")
        self.start_time_label = ttk.Label(self.search_frame, text="Start Time (e.g., 1300):")
        self.start_time_entry = ttk.Entry(self.search_frame)
        self.end_time_label = ttk.Label(self.search_frame, text="End Time (e.g., 1430):")
        self.end_time_entry = ttk.Entry(self.search_frame)
        self.building_label = ttk.Label(self.search_frame, text="Building (Optional):")
        self.building_var = tk.StringVar()
        self.building_dropdown = ttk.Combobox(self.search_frame, textvariable=self.building_var, state="readonly")
        self.find_button = ttk.Button(self.search_frame, text="Find Available Rooms", command=self.handle_find_empty)
        
        self.check_room_frame = ttk.LabelFrame(root, text="Check a Specific Room", padding="10")
        self.classroom_label = ttk.Label(self.check_room_frame, text="Classroom (e.g., CBA-123):")
        self.classroom_entry = ttk.Entry(self.check_room_frame)
        self.check_button = ttk.Button(self.check_room_frame, text="Check Availability", command=self.handle_check_room)
        
        self.results_frame = ttk.LabelFrame(root, text="Results", padding="10")
        self.results_listbox = tk.Listbox(self.results_frame)
        self.results_scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.config(yscrollcommand=self.results_scrollbar.set)
        
        self.copy_button = ttk.Button(root, text="Copy Results to Clipboard", command=self.handle_copy_results)

        # --- NEW: Disclaimer Label ---
        disclaimer_text = "This app is based on the official CSULB Fall 2025 schedule of classes made by administration. Do not completely rely on it as it cannot predict club activities, other students, guest speakers, on-campus events, etc. Use at your own discretion."
        self.disclaimer_label = ttk.Label(root, text=disclaimer_text, wraplength=480, justify=tk.CENTER, font=("TkDefaultFont", 10))

        self.status_label = ttk.Label(root, text="Ready", padding="5", relief=tk.SUNKEN)

        # --- Layout ---
        self.update_frame.pack(fill=tk.X, padx=10, pady=5)
        self.update_button.pack(side=tk.LEFT); self.last_updated_label.pack(side=tk.RIGHT)
        
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        self.search_frame.columnconfigure(1, weight=1)
        self.day_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W); self.day_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.start_time_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W); self.start_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.end_time_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W); self.end_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.building_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W); self.building_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        self.find_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.check_room_frame.pack(fill=tk.X, padx=10, pady=5)
        self.check_room_frame.columnconfigure(1, weight=1)
        self.classroom_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W); self.classroom_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.check_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y); self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.copy_button.pack(pady=5)
        
        # --- NEW: Layout for Disclaimer ---
        self.disclaimer_label.pack(fill=tk.X, padx=10, pady=(5, 10))

        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.initialize_app()

    def initialize_app(self):
        # ... (unchanged) ...
        database.setup_database()
        self.update_building_dropdown()
        self.update_timestamp()
    def update_timestamp(self):
        # ... (unchanged) ...
        if os.path.exists(database.DATABASE_FILE):
            mod_time = os.path.getmtime(database.DATABASE_FILE)
            self.last_updated_label.config(text=f"Last Updated: {datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')}")
    def update_building_dropdown(self):
        # ... (unchanged) ...
        buildings = database.get_all_buildings()
        self.building_dropdown['values'] = ["All Buildings"] + buildings
        self.building_var.set("All Buildings")

    def start_update_thread(self):
        self.scraping_in_progress = True
        self.update_button.config(state=tk.DISABLED); self.find_button.config(state=tk.DISABLED); self.check_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.handle_update)
        thread.start()
        self.check_progress_queue()
    def check_progress_queue(self):
        try:
            message = self.progress_queue.get_nowait()
            self.status_label.config(text=message)
        except queue.Empty:
            pass
        finally:
            if self.scraping_in_progress: self.root.after(100, self.check_progress_queue)

    def handle_update(self):
        all_classes = scraper.get_all_class_schedules(progress_queue=self.progress_queue)
        # --- MODIFIED: Pass class count to on_update_complete ---
        if all_classes:
            database.save_classes_to_db(all_classes)
            self.root.after(0, self.on_update_complete, len(all_classes))
        else:
            self.root.after(0, self.on_update_failed)

    def on_update_complete(self, num_classes_found): # --- MODIFIED: Accept argument ---
        self.scraping_in_progress = False
        # --- MODIFIED: Update status bar with class count ---
        self.status_label.config(text=f"Update complete. {num_classes_found} classes found. Ready.")
        self.update_timestamp(); self.update_building_dropdown()
        self.update_button.config(state=tk.NORMAL); self.find_button.config(state=tk.NORMAL); self.check_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "Class data has been updated successfully.")

    def on_update_failed(self):
        self.scraping_in_progress = False
        self.status_label.config(text="Update failed. Please check connection.")
        self.update_button.config(state=tk.NORMAL); self.find_button.config(state=tk.NORMAL); self.check_button.config(state=tk.NORMAL)
        messagebox.showerror("Error", "Failed to scrape class data.")
    
    def _validate_time_inputs(self):
        # ... (unchanged) ...
        start_time_str, end_time_str = self.start_time_entry.get(), self.end_time_entry.get()
        try:
            start_time, end_time = int(start_time_str), int(end_time_str)
            if start_time >= end_time: messagebox.showerror("Input Error", "Start time must be before end time."); return None, None
            return start_time, end_time
        except ValueError: messagebox.showerror("Input Error", "Please enter valid numbers for start and end times (e.g., 1300)."); return None, None

    def handle_find_empty(self):
        # ... (unchanged) ...
        day_abbr = self.DAY_MAP[self.day_var.get()]
        start_time, end_time = self._validate_time_inputs()
        if start_time is None: return
        building_filter = None if self.building_var.get() == "All Buildings" else self.building_var.get()
        empty_rooms = database.find_empty_rooms(day_abbr, start_time, end_time, building_filter)
        self.results_frame.config(text=f"Results ({len(empty_rooms)} empty rooms found)")
        self.results_listbox.delete(0, tk.END)
        if not empty_rooms: self.results_listbox.insert(tk.END, "No empty rooms found for this time slot.")
        else:
            for room in empty_rooms: self.results_listbox.insert(tk.END, room)

    def handle_check_room(self):
        day_abbr = self.DAY_MAP[self.day_var.get()]
        start_time, end_time = self._validate_time_inputs()
        if start_time is None: return
        classroom = self.classroom_entry.get()
        if not classroom or '-' not in classroom: messagebox.showerror("Input Error", "Please enter a valid classroom name in the format 'BUILDING-ROOM'."); return
        schedule = database.find_room_schedule(day_abbr, start_time, end_time, classroom)
        self.results_listbox.delete(0, tk.END)
        self.results_frame.config(text=f"Schedule for {classroom.upper()}")
        if not schedule: self.results_listbox.insert(tk.END, f"{classroom.upper()} is AVAILABLE during this time.")
        else:
            self.results_listbox.insert(tk.END, f"{classroom.upper()} is OCCUPIED by:")
            # --- MODIFIED: Use multiple inserts for proper formatting ---
            for s in schedule:
                self.results_listbox.insert(tk.END, f"  - {s['course_title']}")
                self.results_listbox.insert(tk.END, f"    Instructor: {s['instructor']}")
                self.results_listbox.insert(tk.END, f"    Time: {s['start_time']} - {s['end_time']}")

    def handle_copy_results(self):
        # ... (unchanged) ...
        results = self.results_listbox.get(0, tk.END)
        if results:
            self.root.clipboard_clear(); self.root.clipboard_append("\n".join(results))
            self.status_label.config(text="Results copied to clipboard!")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomFinderApp(root)
    root.mainloop()