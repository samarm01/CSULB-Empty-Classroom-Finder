import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime # --- THIS IS THE FIX ---

# --- Configuration & All Helper functions (_parse_..., fetch..., extract..., scrape...) are UNCHANGED ---
SEMESTER = "Spring"
YEAR = "2026"
BASE_SCHEDULE_URL = f"https://web.csulb.edu/depts/enrollment/registration/class_schedule/{SEMESTER}_{YEAR}/By_Subject/"
def _parse_days(day_str): return re.findall('M|Tu|W|Th|F|Sa|Su', day_str)
def _parse_time(time_str):
    time_str = time_str.strip()
    if 'TBA' in time_str or '-' not in time_str: return None, None
    try:
        start_str, end_str = [t.strip() for t in time_str.split('-')]
        def convert_to_24hr(t_str, is_pm):
            num = int(re.sub(r'[^0-9]', '', t_str))
            if ':' not in t_str: num *= 100
            if is_pm and num < 1200: return num + 1200
            if not is_pm and num >= 1200: return num - 1200
            return num
        end_is_pm = 'PM' in end_str.upper()
        start_is_pm_explicit = 'PM' in start_str.upper()
        start_is_pm_implicit = end_is_pm and not ('AM' in start_str.upper())
        start_is_pm = start_is_pm_explicit or start_is_pm_implicit
        start_time, end_time = convert_to_24hr(start_str, start_is_pm), convert_to_24hr(end_str, end_is_pm)
        if start_is_pm_implicit and not start_is_pm_explicit and start_time > end_time:
            start_time -= 1200
        return start_time, end_time
    except (ValueError, IndexError): return None, None
def _parse_location(loc_str):
    loc_str = loc_str.strip()
    if 'TBA' in loc_str or 'ONLINE' in loc_str or '-' not in loc_str: return None, None
    try:
        building, room = loc_str.split('-', 1)
        return building.strip(), room.strip()
    except IndexError: return None, None
def fetch_main_page_content():
    try:
        main_url = f"{BASE_SCHEDULE_URL}index.html"
        response = requests.get(main_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException: return None
def extract_subject_links(html_content):
    if not html_content: return []
    soup = BeautifulSoup(html_content, "html.parser")
    subject_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.html') and href[:-5].isupper():
            subject_links.append(f"{BASE_SCHEDULE_URL}{href}")
    return subject_links
def scrape_subject_page(subject_url):
    try:
        response = requests.get(subject_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException: return []
    soup = BeautifulSoup(response.text, 'html.parser')
    class_schedules = []
    course_blocks = soup.find_all('div', class_='courseBlock')
    if not course_blocks: return []
    for block in course_blocks:
        header = block.find('div', class_='courseHeader')
        if not header or not header.find('h4'): continue
        course_code, course_title_text = header.find('span', class_='courseCode').text.strip(), header.find('span', class_='courseTitle').text.strip()
        full_title = f"{course_code} - {course_title_text}"
        table = block.find('table', class_='sectionTable')
        if not table: continue
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 9:
                days_text, time_text, location_text, instructor_text = columns[5].text.strip(), columns[6].text.strip(), columns[8].text.strip(), columns[9].text.strip()
                days, (start_time, end_time), (building, room) = _parse_days(days_text), _parse_time(time_text), _parse_location(location_text)
                if building and room and start_time is not None:
                    class_schedules.append({"course_title": full_title, "days": days, "start_time": start_time, "end_time": end_time, "building": building, "room": room, "instructor": instructor_text})
    return class_schedules
def get_all_class_schedules():
    print("--- Starting Full Scrape Process ---")
    main_html = fetch_main_page_content()
    if not main_html:
        print("Error: Could not fetch the main page. Halting.")
        return []
    subject_links = extract_subject_links(main_html)
    if not subject_links:
        print("Error: Could not find any subject links. Halting.")
        return []
    total_subjects = len(subject_links)
    print(f"Found {total_subjects} subjects to scrape.")
    all_classes = []
    for i, link in enumerate(subject_links):
        filename = link.split('/')[-1]
        print(f"({i+1}/{total_subjects}) Scraping: {filename}")
        schedules = scrape_subject_page(link)
        all_classes.extend(schedules)
        time.sleep(0.05)
    print(f"\n--- Full Scrape Complete ---\nTotal physical class sessions found: {len(all_classes)}")
    return all_classes

def save_data_to_json(class_list, filename="schedule.json"):
    buildings = sorted(list(set(c['building'] for c in class_list)))
    
    final_data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "buildings": buildings,
        "classes": class_list
    }

    with open(filename, 'w') as f:
        json.dump(final_data, f, indent=2)
    print(f"Successfully saved all data to {filename}")

if __name__ == "__main__":
    all_class_data = get_all_class_schedules()
    if all_class_data:
        save_data_to_json(all_class_data)