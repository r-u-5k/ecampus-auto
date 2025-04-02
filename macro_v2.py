import threading
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import params as pa


# 각 강의를 별도의 크롬 창에서 실행하는 함수
def play_lecture_concurrent(lecture_info):
    driver = driver_setting(pa.CHROME_DRIVER_PATH)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["https://accessone.hellolms.com/*"]})
    try:
        # 로그인
        driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
        time.sleep(1)
        driver.find_element(By.XPATH, "//input[@id='usr_id']").send_keys(pa.userid)
        driver.find_element(By.XPATH, "//input[@id='usr_pwd']").send_keys(pa.password)
        driver.find_element(By.XPATH, "//*[@id='login_btn']").click()
        time.sleep(1)

        # 해당 강좌 선택
        WebDriverWait(driver, 30).until(
            ec.element_to_be_clickable((By.XPATH, f"//em[contains(text(), '{lecture_info['course_name']}')]"))
        ).click()
        time.sleep(1)

        # 1주차 페이지로 이동
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]").click()
        time.sleep(1)

        # 해당 주차 클릭 (lecture_info['week_id']는 예를 들어 "1"과 같이 숫자만 담겨 있다고 가정)
        driver.find_element(By.ID, f"week_{lecture_info['week_id']}").click()
        time.sleep(1)

        # 해당 차시 및 강의 선택
        base_xpath = f"/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div[{lecture_info['session_index']}]/div/ul/li[1]/ol/li[5]/div"
        lecture = driver.find_element(By.XPATH, f"{base_xpath}/div[{lecture_info['lecture_index']}]")
        # 강의명 클릭 → 강의 수강 시작
        lecture.find_element(By.XPATH, "./div[1]/div/span").click()
        print(f"{lecture_info['week_id']}주차, {lecture_info['session_index']}차시, {lecture_info['lecture_index']}강 시작")

        # 남은 강의 시간 대기 (여유시간 10초 포함)
        time.sleep(lecture_info['remain_seconds'] + 10)

        # 강의 종료 처리
        while True:
            driver.find_element(By.ID, "close_").click()
            try:
                WebDriverWait(driver, 5).until(ec.alert_is_present())
                alert = Alert(driver)
                alert.dismiss()
                time.sleep(30)
            except TimeoutException:
                break

        print(f"{lecture_info['week_id']}주차 {lecture_info['session_index']}차시 {lecture_info['lecture_index']}강 수강 완료")
        time.sleep(2)
    except Exception as e:
        print("강의 실행 중 오류 발생:", e)
    finally:
        driver.quit()

# 원래 코드 내에서 lecture_elements를 병렬로 실행하도록 수정한 macro 함수 예시
def macro(course_name):
    driver = driver_setting(pa.CHROME_DRIVER_PATH)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["https://accessone.hellolms.com/*"]})
    lecture_threads = []  # 강의별 스레드를 담을 리스트
    try:
        driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
        time.sleep(1)
        # 로그인
        driver.find_element(By.XPATH, "//input[@id='usr_id']").send_keys(pa.userid)
        driver.find_element(By.XPATH, "//input[@id='usr_pwd']").send_keys(pa.password)
        driver.find_element(By.XPATH, "//*[@id='login_btn']").click()
        time.sleep(1)

        # 해당 강좌 선택
        WebDriverWait(driver, 30).until(
            ec.element_to_be_clickable((By.XPATH, f"//em[contains(text(), '{course_name}')]"))
        ).click()
        time.sleep(1)

        # 1주차 페이지로 이동
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]").click()
        time.sleep(1)

        # 주차별 강의 리스트 구성
        week_elements = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ibox3 wb')]"))
        )

        for week_element in week_elements:
            # 강의 진행률 확인 ("x/y" 형식)
            x, y = week_element.find_element(By.CLASS_NAME, "wb-status").text.strip().split("/")
            if x != y:  # 아직 수강하지 않은 주차라면
                week_id = week_element.get_attribute("id")[5:]  # 예: "week_1" → "1"
                print(f"수강할 강의: {week_id}주차")
                week_element.click()
                time.sleep(1)

                session_elements = WebDriverWait(driver, 10).until(
                    ec.presence_of_all_elements_located(
                        (By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div")
                    )
                )
                print(f"총 {len(session_elements)}차시")
                for session_index in range(1, len(session_elements) + 1):
                    base_xpath = f"/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div[{session_index}]/div/ul/li[1]/ol/li[5]/div"
                    lecture_elements = driver.find_elements(By.XPATH, f"{base_xpath}/div")
                    for lecture_index in range(1, len(lecture_elements) + 1):
                        lecture = driver.find_element(By.XPATH, f"{base_xpath}/div[{lecture_index}]")
                        lecture_name_text = lecture.find_element(By.XPATH, "./div[1]/div/span").text
                        print(f"강의명: {lecture_name_text}")

                        time_element = lecture.find_element(By.XPATH, "./div[2]/div[3]")
                        # 출첵 반영 안 되는 강의라면 건너뜀
                        if time_element.text == "":
                            continue
                        total_seconds = cal_total_time(time_element)
                        remain_seconds = cal_remain_time(time_element, total_seconds)
                        progress_str = lecture.find_element(By.XPATH, "./div[2]/div[2]").text
                        if progress_str == "100%":
                            continue

                        # 강의 정보를 딕셔너리로 구성
                        lecture_info = {
                            "course_name": course_name,
                            "week_id": week_id,  # 숫자 또는 문자열로 사용 (예: "1")
                            "session_index": session_index,
                            "lecture_index": lecture_index,
                            "remain_seconds": remain_seconds
                        }

                        # 각 강의를 별도의 스레드로 실행 (동시에 수강 시작)
                        t = threading.Thread(target=play_lecture_concurrent, args=(lecture_info,))
                        t.start()
                        lecture_threads.append(t)
                        print(f"{week_id}주차 {session_index}차시 {lecture_index}강 스레드 시작")
    except Exception as e:
        print("수강 강의 목록 구성 중 오류 발생:", e)
    finally:
        driver.quit()

    # 모든 강의 스레드가 종료될 때까지 대기
    for t in lecture_threads:
        t.join()


def driver_setting(download_path):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"download.default.directory": download_path,
                                              "download.prompt_for_download": False,
                                              "download.directory_upgrade": True,
                                              "safebrowsing.for_trusted_sources_enabled": False,
                                              "safebrowsing.enabled": False})

    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-sha-usage")

    service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.implicitly_wait(1)

    return driver


def cal_remain_time(time_element, total_seconds):
    studied_time_str = time_element.text.split("/")[0].strip()
    if len(studied_time_str) == 7:
        studied_time_obj = datetime.strptime(studied_time_str, "%H:%M:%S")
        studied_seconds = studied_time_obj.hour * 3600 + studied_time_obj.minute * 60 + studied_time_obj.second
    else:
        studied_time_obj = datetime.strptime(studied_time_str, "%M:%S")
        studied_seconds = studied_time_obj.minute * 60 + studied_time_obj.second
    remain_seconds = total_seconds - studied_seconds
    return remain_seconds


def cal_total_time(time_element):
    time_str = time_element.text.split("/")[2].strip()
    if len(time_str) == 7:
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    else:
        time_obj = datetime.strptime(time_str, "%M:%S")
        total_seconds = time_obj.minute * 60 + time_obj.second
    return total_seconds


if __name__ == "__main__":
    macro(input())
