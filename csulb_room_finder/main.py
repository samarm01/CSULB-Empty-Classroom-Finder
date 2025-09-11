import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class RoomFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSULB Room Finder")
        self.root.geometry("450x550")

        # --- Create UI Elements ---

        self.update_frame = ttk.Frame(root, padding="10")
        self.update_button = ttk.Button(self.update_frame, text="Update Class Data", command=self.handle_update)
        self.last_updated_label = ttk.Label(self.update_frame, text="Last Updated: Never")

        self.search_frame = ttk.LabelFrame(root, text="Find an Empty Room", padding="10")
        
        self.day_label = ttk.Label(self.search_frame, text="Day:")
        self.day_var = tk.StringVar()
        self.day_dropdown = ttk.Combobox(
            self.search_frame, 
            textvariable=self.day_var, 
            values=["M", "Tu", "W", "Th", "F", "Sa", "Su"],
            state="readonly"
        )
        self.day_dropdown.set("M")

        self.start_time_label = ttk.Label(self.search_frame, text="Start Time (e.g., 1300):")
        self.start_time_entry = ttk.Entry(self.search_frame)
        self.end_time_label = ttk.Label(self.search_frame, text="End Time (e.g., 1430):")
        self.end_time_entry = ttk.Entry(self.search_frame)

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
        
        # --- THIS IS THE CORRECTED LINE ---
        self.search_frame.columnconfigure(1, weight=1) # Makes the entry widgets expand
        # ----------------------------------

        self.day_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.day_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.start_time_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.end_time_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.find_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def handle_update(self):
        print("Update button clicked!")
        pass

    def handle_find(self):
        print("Find button clicked!")
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomFinderApp(root)
    root.mainloop()