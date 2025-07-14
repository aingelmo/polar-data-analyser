import logging
import time

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from polar.utils import get_filename_from_response, write_to_file

FLOW_URL = "https://flow.polar.com"


class PolarFlowClient:
    def __init__(self, driver: Chrome):
        self.driver = driver

    def login(self, username: str, password: str) -> None:
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        try:
            logging.info(f"Navigating to {FLOW_URL}/login")
            self.driver.get(f"{FLOW_URL}/login")
            logging.info(f"Current URL after navigation: {self.driver.current_url}")
            wait = WebDriverWait(self.driver, 20)
            logging.info("Waiting for username field...")
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            logging.info("Username field found. Entering username.")
            username_field.send_keys(username)
            logging.info("Waiting for password field...")
            password_field = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            logging.info("Password field found. Entering password.")
            password_field.send_keys(password)
            logging.info("Waiting for login button...")
            login_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-testid="login-button"]')
                )
            )
            logging.info("Login button found. Submitting form.")
            login_button.click()
            logging.info("Login form submitted.")
        except Exception as e:
            logging.error(f"Error during login navigation or form interaction: {e}")
            raise

    def get_exercise_ids(self, year: str, month: str) -> list[str]:
        self.driver.get(f"{FLOW_URL}/diary/{year}/month/{month}")
        time.sleep(2)
        elements = self.driver.find_elements(
            By.XPATH, "//div[@class='event event-month exercise']/a"
        )
        logging.info(f"Found {len(elements)} exercise link elements on diary page.")
        prefix = "https://flow.polar.com/training/analysis2/"
        ids = []
        for e in elements:
            href = e.get_attribute("href")
            logging.info(f"Found href: {href}")
            if href and href.startswith(prefix):
                ex_id = href[len(prefix) :]
                if ex_id:
                    ids.append(ex_id)
        logging.info(f"Extracted {len(ids)} exercise IDs: {ids}")
        return ids

    def get_all_exercise_ids_for_year(self, year: str) -> list[str]:
        all_ids = []
        for month in range(1, 13):
            month_str = str(month)
            logging.info(f"Processing month {month_str} of year {year}...")
            ids = self.get_exercise_ids(year, month_str)
            logging.info(f"Found {len(ids)} exercises in month {month_str}.")
            all_ids.extend(ids)
        logging.info(f"Total exercises found for year {year}: {len(all_ids)}")
        return all_ids

    def export_exercise(self, exercise_id: str, output_dir: str) -> None:
        def _load_cookies(session: requests.Session, cookies: list[dict]) -> None:
            for cookie in cookies:
                session.cookies.set(cookie["name"], cookie["value"])

        s = requests.Session()
        _load_cookies(s, self.driver.get_cookies())

        r = s.get(f"{FLOW_URL}/api/export/training/csv/{exercise_id}")
        tcx_data = r.text
        filename = get_filename_from_response(r)
        write_to_file(output_dir, filename, tcx_data)
        print(f"Wrote file {filename}")
