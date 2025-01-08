import time
import sys
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

TIME_OUT_IN_SECONDS = 15


def scrape_udemy_course(url: str) -> dict:
    print("\nCollecting data...")
    driver = webdriver.Chrome()
    driver.get(url)

    course_data = {
        "title": "",
        "sections": []
    }

    try:
        # Wait and click the "Show all sections" button
        try:
            show_all_sections_btn = WebDriverWait(driver, TIME_OUT_IN_SECONDS).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ud-btn.ud-btn-medium.ud-btn-ghost.ud-heading-sm'))
            )
            driver.execute_script("arguments[0].click();", show_all_sections_btn)
            expand_sections_btn = WebDriverWait(driver, TIME_OUT_IN_SECONDS).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-purpose="expand-toggle"]'))
            )
            driver.execute_script("arguments[0].click();", expand_sections_btn)
        except TimeoutException:
            sys.exit(f"Timeout {TIME_OUT_IN_SECONDS} seconds waiting for 'Expand sections' button to be clickable.")

        time.sleep(2)
        content = driver.page_source

    except Exception as e:
        sys.exit(f"An unexpected error occurred: {e}")

    finally:
        driver.quit()

    soup = BeautifulSoup(content, 'html.parser')

    course_title_tag = soup.find('h1', class_='ud-heading-xl clp-lead__title clp-lead__title--small')
    course_title = course_title_tag.text.strip() if course_title_tag else 'No title found'
    course_data["title"] = course_title

    sections = soup.find_all('div', class_='accordion-panel-module--panel--Eb0it section--panel--qYPjj')

    for section in sections:
        section_title_tag = section.find('span', class_='section--section-title--svpHP')
        section_title = section_title_tag.text.strip() if section_title_tag else 'No section title found'

        section_title = section_title.replace(", ", "&")

        time_section = section.find('span', class_='ud-text-sm section--hidden-on-mobile---ITMr '
                                                   'section--section-content--2mUJ7').find('span').text

        section_data = {
            "section_title": section_title,
            "time": time_section,
            "lectures": []
        }

        lectures = section.find_all('div', class_='ud-block-list-item-content')

        for lecture in lectures:
            lecture_title_tag = lecture.find('span', class_='section--item-title--EWIuI')

            if lecture_title_tag is None:
                lecture_title_tag = lecture.find('button', class_='section--item-title--EWIuI')
            lecture_title = lecture_title_tag.text.strip() if lecture_title_tag else 'No lecture title found'

            duration_tag = lecture.find('span', class_='section--hidden-on-mobile---ITMr '
                                                       'section--item-content-summary--Aq9em')
            duration = duration_tag.text.strip()

            if "question" in duration or "questions" in duration:
                duration = "30:00"

            lecture_data = {
                "lecture_title": lecture_title,
                "duration": duration
            }
            section_data["lectures"].append(lecture_data)
        course_data["sections"].append(section_data)

    print(f"\nData from {url} has been collected successfully")

    file_name = "course.json"
    with open(file_name, "w") as file:
        json.dump(course_data, file, indent=4)
    print("\nCourse data has been saved successfully to " + file_name)

    return course_data
