import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import params as pa


def driver_setting(DownloadPath):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"download.default.directory": DownloadPath,
                                              "download.prompt_for_download": False,
                                              "download.directory_upgrade": True,
                                              "safebrowsing.for_trusted_sources_enabled": False,
                                              "safebrowsing.enabled": False})

    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-sha-usage")

    service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(1)

    return driver


def macro(lecture_name):
    driver = driver_setting(pa.CHROME_DRIVER_PATH)
    try:
        driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
        time.sleep(1)

        # 로그인
        driver.find_element(By.XPATH, "//input[@id='usr_id']").send_keys(pa.userid)
        driver.find_element(By.XPATH, "//input[@id='usr_pwd']").send_keys(pa.password)
        driver.find_element(By.XPATH, "//*[@id='login_btn']").click()
        time.sleep(1)
        print("로그인 성공")

        # 강의 페이지로 이동
        WebDriverWait(driver, 30).until(  # 대기 시간 증가
            EC.element_to_be_clickable((By.XPATH, f"//em[contains(text(), '{lecture_name}')]"))
        ).click()
        time.sleep(1)

        # 1주차 페이지로 이동
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]").click()
        time.sleep(1)

        # 강의 전체 주차 수를 가져옴
        weeks = driver.find_elements(By.XPATH, "//div[contains(@class, 'ibox3 wb')]")
        print("총 " + str(len(weeks)) + "주차")

        for week in weeks:
            x, y = week.find_element(By.CLASS_NAME, "wb-status").text.strip().split("/")

            if x != y:
                week_id = week.get_attribute("id")
                driver.find_element(By.ID, week_id).click()
                time.sleep(1)

                session_elements = driver.find_elements(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div")

                for session in session_elements:
                    lecture_elements = session.find_elements(By.XPATH, "./div/ul/li[1]/ol/li[5]/div/div")
                    for lecture in lecture_elements:
                        # 06.사용자정의함수와 모듈 활용하기
                        # 88%
                        # 29:58 / 0:00 / 33:51
                        lecture_name = lecture.find_element(By.XPATH, "./div[1]/div/span")
                        print(f"강의명: {lecture_name.text}")

                        time_element = lecture.find_element(By.XPATH, "./div[2]/div[3]")

                        # 출첵 반영 안 되는 강의인 경우 넘어감
                        if time_element.text == "":
                            continue

                        # 전체 강의 시간
                        time_str = time_element.text.split("/")[2].strip()
                        if len(time_str) == 7:
                            time_obj = datetime.strptime(time_str, "%H:%M:%S")
                            total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
                        else:
                            time_obj = datetime.strptime(time_str, "%M:%S")
                            total_seconds = time_obj.minute * 60 + time_obj.second
                        print(f"전체 강의 시간: {total_seconds}초")

                        # 남은 강의 시간
                        studied_time_str = time_element.text.split("/")[0].strip()
                        if len(studied_time_str) == 7:
                            studied_time_obj = datetime.strptime(studied_time_str, "%H:%M:%S")
                            studied_seconds = studied_time_obj.hour * 3600 + studied_time_obj.minute * 60 + studied_time_obj.second
                        else:
                            studied_time_obj = datetime.strptime(studied_time_str, "%M:%S")
                            studied_seconds = studied_time_obj.minute * 60 + studied_time_obj.second
                        remain_seconds = total_seconds - studied_seconds
                        print(f"남은 강의 시간: {remain_seconds}초")

                        # 이미 강의 진도율이 100%인 경우 다음 강의로 넘어감
                        progress_element = lecture.find_element(By.XPATH, "./div[2]/div[2]")
                        progress_str = progress_element.text
                        print(f"강의 진도율: {progress_str}")
                        if progress_str == "100%":
                            continue

                        # 강의 클릭
                        lecture_name.click()
                        print("열심히 강의 수강 중..")
                        # time.sleep(remain_seconds + 30)

                        # 강의 종료
                        driver.find_element(By.ID, "close_").click()
                        try:
                            WebDriverWait(driver, 10).until(EC.alert_is_present())
                            alert = Alert(driver)
                            alert.accept()
                        except TimeoutException:
                            pass

                        print("강의 수강 완료")
                        driver.refresh()

    except TimeoutException:
        print("시간 초과")
    except NoSuchElementException as e:
        print(f"해당 요소가 없음: {str(e)}")
    except StaleElementReferenceException:
        print(f"Stale element 오류 발생")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    macro("온라인학습법특강 7")
