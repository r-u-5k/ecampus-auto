import time
from datetime import timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException


class Lecture:
    def __init__(self, driver, base_xpath, index):
        self.driver = driver
        self.base_xpath = base_xpath
        self.index = index
        self.name = self.get_lecture_name()

    def get_lecture_name(self):
        lecture_name = self.driver.find_element(By.XPATH, f"{self.base_xpath}[{self.index}]/div[1]/div/span")
        return lecture_name.text

    def needs_watching(self):
        time_element = self.driver.find_element(By.XPATH, f"{self.base_xpath}[{self.index}]/div[2]/div[3]")
        if time_element.text == "":
            return False

        progress_element = self.driver.find_element(By.XPATH, f"{self.base_xpath}[{self.index}]/div[2]/div[2]")
        progress_str = progress_element.text
        print(f"강의 진도율: {progress_str}")
        return progress_str != "100%"

    def get_remaining_time(self):
        time_element = self.driver.find_element(By.XPATH, f"{self.base_xpath}[{self.index}]/div[2]/div[3]")
        time_parts = time_element.text.split('/')

        def parse_time(time_str):
            parts = time_str.strip().split(':')
            if len(parts) == 2:
                return timedelta(minutes=int(parts[0]), seconds=int(parts[1]))
            elif len(parts) == 3:
                return timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=int(parts[2]))
            else:
                raise ValueError(f"Unexpected time format: {time_str}")

        studied_time = parse_time(time_parts[0])
        total_time = parse_time(time_parts[2])

        remaining_time = total_time - studied_time
        return remaining_time.total_seconds()

    def watch(self):
        remain_seconds = self.get_remaining_time()
        print(f"남은 강의 시간: {int(remain_seconds)}초")

        lecture_element = self.driver.find_element(By.XPATH, f"{self.base_xpath}[{self.index}]/div[1]/div/span")
        lecture_element.click()
        print("열심히 강의 수강 중..")
        time.sleep(remain_seconds + 60)

        self.driver.find_element(By.ID, "close_").click()
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = Alert(self.driver)
            alert.accept()
        except TimeoutException:
            pass

        print(f"{self.name} 강의 수강 완료")
        time.sleep(1)
