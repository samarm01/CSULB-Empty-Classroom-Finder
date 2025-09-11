import requests
from bs4 import BeautifulSoup
import re
import time

# --- Configuration ---
SEMESTER = "Fall"
YEAR = "2025"
# ---------------------

BASE_SCHEDULE_URL = f"https://web.csulb.edu/depts/enrollment/registration/class_schedule/{SEMESTER}_{YEAR}/By_Subject/"

# All helper functions (_parse_days, _parse_time, _parse_location) are unchanged
def _parse_days(day_str):
    return re.findall('M|Tu|W|Th|F|Sa|Su', day_str)

def _parse_time(time_str):
    time_str = time_str.strip()
    if 'TBA' in time_str or '-' not in time_str:
        return None, None
    try:
        start_str, end_str = [t.strip() for t in time_str.split('-')]
        end_is_pm = 'PM' in end_str.upper()
        start_time_num = int(re.sub(r'[^0-9]', '', start_str))
        if ':' not in start_str: start_time_num *= 100
        end_time_num = int(re.sub(r'[^0-9]', '', end_str))
        if ':' not in end_str.replace('AM','').replace('PM',''): end_time_num *= 100
        start_hour = start_time_num // 100
        start_is_pm = False
        if end_is_pm and start_hour < 12 and (start_hour < 8 or start_hour < (end_time_num//100)):
             start_is_pm = True
        if start_is_pm and start_time_num < 1200: start_time_num += 1200
        elif not start_is_pm and start_time_num >= 1200: start_time_num -= 1200
        if end_is_pm and end_time_num < 1200: end_time_num += 1200
        elif not end_is_pm and end_time_num >= 1200: end_time_num -= 1200
        return start_time_num, end_time_num
    except (ValueError, IndexError):
        return None, None

def _parse_location(loc_str):
    loc_str = loc_str.strip()
    if 'TBA' in loc_str or 'ONLINE' in loc_str or '-' not in loc_str:
        return None, None
    try:
        building, room = loc_str.split('-', 1)
        return building.strip(), room.strip()
    except IndexError:
        return None, None

def fetch_main_page_content():
    main_url = f"{BASE_SCHEDULE_URL}index.html"
    try:
        response = requests.get(main_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the main page: {e}")
        return None

def extract_subject_links(html_content):
    if not html_content: return []
    soup = BeautifulSoup(html_content, "html.parser")
    subject_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.html') and href[:-5].isupper():
            full_url = f"{BASE_SCHEDULE_URL}{href}"
            subject_links.append(full_url)
    return subject_links

def scrape_subject_page(subject_url):
    print(f"  Scraping: {subject_url.split('/')[-1]}")
    try:
        response = requests.get(subject_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    class_schedules = []
    course_blocks = soup.find_all('div', class_='courseBlock')
    if not course_blocks: return []

    for block in course_blocks:
        header = block.find('div', class_='courseHeader')
        if not header or not header.find('h4'): continue
        course_code = header.find('span', class_='courseCode').text.strip()
        course_title_text = header.find('span', class_='courseTitle').text.strip()
        full_title = f"{course_code} - {course_title_text}"
        table = block.find('table', class_='sectionTable')
        if not table: continue

        for row in table.find_all('tr'):
            columns = row.find_all('td')
            # Now we expect at least 10 columns to get the instructor
            if len(columns) > 9:
                days_text = columns[5].text.strip()
                time_text = columns[6].text.strip()
                location_text = columns[8].text.strip()
                instructor_text = columns[9].text.strip() # <--- NEW LINE

                days = _parse_days(days_text)
                start_time, end_time = _parse_time(time_text)
                building, room = _parse_location(location_text)
                
                if building and room and start_time is not None:
                    class_schedules.append({
                        "course_title": full_title,
                        "days": days,
                        "start_time": start_time,
                        "end_time": end_time,
                        "building": building,
                        "room": room,
                        "instructor": instructor_text # <--- NEW KEY/VALUE PAIR
                    })
    return class_schedules

def get_all_class_schedules():
    print("--- Starting Full Scrape Process ---")
    main_html = fetch_main_page_content()
    if not main_html:
        print("Halting process: Could not fetch the main page.")
        return []
    
    subject_links = extract_subject_links(main_html)
    if not subject_links:
        print("Halting process: Could not find any subject links.")
        return []
    print(f"Found {len(subject_links)} subject pages to scrape.")
    
    all_classes = []
    for link in subject_links:
        schedules = scrape_subject_page(link)
        all_classes.extend(schedules)
        time.sleep(0.1)
        
    print(f"\n--- Full Scrape Complete ---")
    print(f"Total physical class sessions found: {len(all_classes)}")
    return all_classes

# --- Testing Block ---
if __name__ == "__main__":
    all_schedules = get_all_class_schedules()
    if all_schedules:
        print("\n--- Sample of Final Aggregated Data (with Instructor) ---")
        for i, class_info in enumerate(all_schedules[:5]):
            print(f"{i+1}: {class_info}")
        print("...")
        for i, class_info in enumerate(all_schedules[-5:]):
             print(f"{len(all_schedules)-5+i+1}: {class_info}")
        print("----------------------------------------------------------")