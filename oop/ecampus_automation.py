import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lecture import Lecture


class ECampusAutomation:
    def __init__(self, driver):
        self.driver = driver

    def login(self, userid, password):
        self.driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//input[@id='usr_id']").send_keys(userid)
        self.driver.find_element(By.XPATH, "//input[@id='usr_pwd']").send_keys(password)
        self.driver.find_element(By.XPATH, "//*[@id='login_btn']").click()
        time.sleep(1)
        print("로그인 성공")

    def navigate_to_lecture_page(self, lecture_name):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//em[contains(text(), '{lecture_name}')]"))
            ).click()
            time.sleep(1)
            print(f"{lecture_name} 강의 페이지로 이동 성공")
        except Exception as e:
            print(f"{lecture_name} 강의를 찾을 수 없음: {str(e)}")

    def get_total_weeks(self):
        weeks = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ibox3 wb')]")
        print(f"총 {len(weeks)}주차")
        return weeks

    def process_week(self, week):
        status = week.find_element(By.CLASS_NAME, "wb-status").text.strip()
        if status == "0/1":
            week_id = week.get_attribute("id")
            self.driver.find_element(By.ID, week_id).click()
            time.sleep(1)
            return self.process_lectures(week_id)
        return []

    def process_lectures(self, week_id):
        base_xpath = "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div/div/ul/li[1]/ol/li[5]/div/div"
        div_elements = self.driver.find_elements(By.XPATH, f"{base_xpath}")
        print(f"{str(week_id)[5:]}주차 강의: 총 {len(div_elements)}개")

        completed_lectures = []
        for index, div in enumerate(div_elements, start=1):
            lecture = Lecture(self.driver, base_xpath, index)
            if lecture.needs_watching():
                lecture.watch()
                completed_lectures.append(lecture.name)
        return completed_lectures

    def watch_specific_lecture(self, lecture_name):
        self.navigate_to_lecture_page(lecture_name)
        weeks = self.get_total_weeks()
        for week in weeks:
            completed_lectures = self.process_week(week)
            if completed_lectures:
                print(f"이번 주 완료한 강의: {', '.join(completed_lectures)}")
                if lecture_name in completed_lectures:
                    print(f"{lecture_name} 강의 시청 완료")
                    return True
        print(f"{lecture_name} 강의를 찾을 수 없거나 이미 시청 완료되었습니다.")
        return False
