---

# CSULB Empty Classroom Finder

A simple desktop application for Windows that helps students and faculty at California State University, Long Beach find empty classrooms based on the official class schedule.




**Features:**

*   **Find Empty Classrooms:** Select a day, a time slot, and an optional building to get a list of all physically available classrooms.
*   **Check Specific Rooms:** Verify the schedule for a single classroom to see if it's occupied during a specific time, and if so, by which class and instructor.
*   **Live Data Updates:** Scrapes the official CSULB Schedule of Classes website to ensure the data is current. The user can refresh the data at any time.
*   **User-Friendly Interface:** A clean and straightforward UI that provides all functionality in a single window.
*   **Copy Results:** Easily copy the list of available rooms to your clipboard.

---

## How to Download & Use (For General Users)

You can download a standalone executable file (`.exe`) that runs on Windows without needing to install Python or any other dependencies.

1.  **Go to the Releases Page:** Click on the **[Releases](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/releases)** tab on the right side of this GitHub page.

2.  **Download the EXE:** Under the latest release (e.g., "Version 1.0"), find the **`CSULB Room Finder.exe`** file and download it.

3.  **Run the Application:** Double-click the downloaded `.exe` file to run the application. No installation is required.

*(**Note to you:** To make this work, you need to create a "Release" on GitHub. Go to your repository, click "Releases" on the right sidebar, and "Create a new release." Give it a version number like `v1.0`, and then upload the `CSULB Room Finder.exe` file from your `dist` folder as a binary asset.)*

---

## How It Works (For Developers)

This application is built with Python and follows a "scrape-and-search" architecture composed of three main parts:

1.  **The Scraper (`scraper.py`):**
    *   Uses the `requests` library to download the HTML from the official CSULB "Schedule of Classes by Subject" pages.
    *   Uses `BeautifulSoup4` to parse the complex HTML structure, extracting details for every class session (course title, day, time, location, instructor).
    *   Reports its progress to the main UI in real-time using a thread-safe `queue`.

2.  **The Database (`database.py`):**
    *   Uses Python's built-in `sqlite3` library to create a simple, local database file (`schedule.db`).
    *   The scraped data is saved to this database, allowing for instant and efficient searching without having to re-scrape the website for every query.
    *   Contains the core logic for finding empty rooms by calculating time-slot overlaps.

3.  **The User Interface (`main.py`):**
    *   A desktop GUI built using Python's native `tkinter` library.
    *   Handles all user input and displays the results from the database.
    *   Uses `threading` to run the scraping process in the background, ensuring the UI never freezes during data updates.

---

## Running from Source

If you want to run the application directly from the source code, you'll need Python 3 installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY
    ```

2.  **Install the required libraries:**
    ```bash
    pip install requests beautifulsoup4
    ```

3.  **Run the main application:**
    ```bash
    python main.py
    ```

## Disclaimer

This app is based on the official CSULB Fall 2025 schedule of classes made by administration. Do not completely rely on it as it cannot predict club activities, other students, guest speakers, on-campus events, etc. Use at your own discretion.
