import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Holds how much time should be waited before throwing an error
# Depends on your internet connections and other factors
TIME_OUT_IN_SECONDS = 15


def scrape_udemy_course(url):
    # Initialize Chrome webdriver
    driver = webdriver.Chrome()
    driver.get(url)

    course_data = {
        "title": "",
        "sections": []
    }

    try:
        # Wait for the button (button that opens all sections) to be clickable
        show_all_sections_btn = WebDriverWait(driver, TIME_OUT_IN_SECONDS).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ud-btn.ud-btn-medium.ud-btn-ghost.ud-heading-sm'))
        )

        # Click the button using JS
        driver.execute_script("arguments[0].click();", show_all_sections_btn)

        # Wait for the button (button that expands all sections) to be clickable
        expand_sections_btn = WebDriverWait(driver, TIME_OUT_IN_SECONDS).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-purpose="expand-toggle"]'))
        )

        # Click the button using JS
        driver.execute_script("arguments[0].click();", expand_sections_btn)

        # Wait for content to load
        time.sleep(2)

        # Get the page source
        content = driver.page_source

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Extract course title
        course_title_tag = soup.find('h1', class_='ud-heading-xl clp-lead__title clp-lead__title--small')
        course_title = course_title_tag.text.strip() if course_title_tag else 'No title found'
        course_data["title"] = course_title
        print(f"Course Title: {course_title}")

        # Extract course content sections
        sections = soup.find_all('div', class_='accordion-panel-module--panel--Eb0it section--panel--qYPjj')

        for section in sections:
            # Extract section title
            section_title_tag = section.find('span', class_='section--section-title--svpHP')
            section_title = section_title_tag.text.strip() if section_title_tag else 'No section title found'

            section_data = {
                "section_title": section_title,
                "lectures": []
            }

            # print(f"SECTION: {section_title}")

            # Extract lectures from each section
            lectures = section.find_all('div', class_='ud-block-list-item-content')

            for lecture in lectures:
                lecture_title_tag = lecture.find('span', class_='section--item-title--EWIuI')
                lecture_title = lecture_title_tag.text.strip() if lecture_title_tag else 'No lecture title found'

                duration_tag = lecture.find('span', class_='section--hidden-on-mobile---ITMr '
                                                           'section--item-content-summary--Aq9em')
                duration = duration_tag.text.strip() if duration_tag else 'No duration found'

                lecture_data = {
                    "lecture_title": lecture_title,
                    "duration": duration
                }

                section_data["lectures"].append(lecture_data)

                # print(f"Lecture: {lecture_title} | Duration: {duration}")

            # print("----------------------------------------")
            course_data["sections"].append(section_data)

    except TimeoutException:
        print(f"Timeout {TIME_OUT_IN_SECONDS} seconds waiting for button to be clickable.")

    finally:
        driver.quit()

    return course_data