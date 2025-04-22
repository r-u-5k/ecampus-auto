import argparse
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def macro(lecture_name, userid, password):
    chrome_path = ChromeDriverManager().install()
    service = Service(chrome_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["https://accessone.hellolms.com/*"]})

    try:
        driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
        time.sleep(1)

        # 로그인
        driver.find_element(By.XPATH, "//input[@id='usr_id']").send_keys(userid)
        driver.find_element(By.XPATH, "//input[@id='usr_pwd']").send_keys(password)
        driver.find_element(By.XPATH, "//*[@id='login_btn']").click()
        time.sleep(1)

        # 강의 페이지로 이동
        WebDriverWait(driver, 30).until(
            ec.element_to_be_clickable((By.XPATH, f"//em[contains(text(), '{lecture_name}')]"))
        ).click()
        time.sleep(1)

        # 1주차 페이지로 이동
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]").click()
        time.sleep(1)

        week_elements = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ibox3 wb')]"))
        )

        for week_index in range(len(week_elements)):
            week_elements = WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ibox3 wb')]"))
            )
            week_index = week_elements[week_index]

            x, y = week_index.find_element(By.CLASS_NAME, "wb-status").text.strip().split("/")

            if x != y:
                week_id = week_index.get_attribute("id")
                print(f"수강할 강의: {week_id[5:]}주차")
                driver.find_element(By.ID, week_id).click()
                time.sleep(1)

                session_elements = WebDriverWait(driver, 10).until(
                    ec.presence_of_all_elements_located(
                        (By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div"))
                )
                print(f"총 {len(session_elements)}차시")
                for session_index in range(1, len(session_elements) + 1):
                    base_xpath = f"/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div[{session_index}]/div/ul/li[1]/ol/li[5]/div"
                    lecture_elements = driver.find_elements(By.XPATH, f"{base_xpath}/div")

                    not_period_div = driver.find_elements(By.XPATH, f"/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div[{session_index}]/div[1]/div")
                    if not_period_div:
                        if not_period_div[0].text == "학습 기간이 아닙니다.":
                            print("학습 기간이 아님")
                            break

                    for lecture_index in range(1, len(lecture_elements) + 1):
                        lecture = driver.find_element(By.XPATH, f"{base_xpath}/div[{lecture_index}]")
                        lecture_name = lecture.find_element(By.XPATH, "./div[1]/div/span")
                        print(f"강의명: {lecture_name.text}")
                        time_element = lecture.find_element(By.XPATH, "./div[2]/div[3]")

                        # 출첵 반영 안 되는 강의인 경우 넘어감
                        if time_element.text == "":
                            continue

                        # 전체 강의 시간
                        total_seconds = cal_total_time(time_element)
                        if total_seconds >= 3600:
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            print(f"전체 강의 시간: {hours}시간 {minutes}분 {seconds}초")
                        else:
                            minutes, seconds = divmod(total_seconds, 60)
                            print(f"전체 강의 시간: {minutes}분 {seconds}초")

                        # 남은 강의 시간
                        remain_seconds = cal_remain_time(time_element, total_seconds)
                        if remain_seconds >= 3600:
                            hours, remainder = divmod(remain_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            print(f"남은 강의 시간: {hours}시간 {minutes}분 {seconds}초")
                        else:
                            minutes, seconds = divmod(remain_seconds, 60)
                            print(f"남은 강의 시간: {minutes}분 {seconds}초")

                        progress_element = lecture.find_element(By.XPATH, "./div[2]/div[2]")
                        progress_str = progress_element.text
                        print(f"강의 진도율: {progress_str}")
                        # 이미 강의 진도율이 100%인 경우 다음 강의로 넘어감
                        if progress_str == "100%":
                            continue

                        # 강의 클릭
                        lecture_name.click()
                        print("열심히 강의 수강 중..")
                        time.sleep(remain_seconds + 30)

                        while True:
                            driver.find_element(By.ID, "close_").click()
                            try:
                                WebDriverWait(driver, 5).until(ec.alert_is_present())
                                alert = Alert(driver)
                                alert.dismiss()
                                time.sleep(20)
                            except TimeoutException:
                                break

                        print(f"{week_id[5:]}주차 {session_index}차시 {lecture_index}강 수강 완료")
                        time.sleep(2)

    except TimeoutException:
        print("에러: 시간 초과")
    except NoSuchElementException as e:
        print(f"에러: {str(e)} 요소가 없음")
    except StaleElementReferenceException:
        print(f"에러: Stale Element")
    except Exception as e:
        print(f"에러: {str(e)}")
    finally:
        driver.quit()


# def driver_setting(download_path):
#     options = webdriver.ChromeOptions()
#     options.add_experimental_option("prefs", {"download.default.directory": download_path,
#                                               "download.prompt_for_download": False,
#                                               "download.directory_upgrade": True,
#                                               "safebrowsing.for_trusted_sources_enabled": False,
#                                               "safebrowsing.enabled": False})
#
#     # options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-sha-usage")
#
#     service = Service()
#
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.implicitly_wait(1)
#
#     return driver


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
    parser = argparse.ArgumentParser(description="폭력예방교육 자동 수강 매크로")
    parser.add_argument("--id", required=True, help="이캠퍼스 아이디")
    parser.add_argument("--pw", required=True, help="이캠퍼스 비밀번호")
    args = parser.parse_args()
    lecture_name = "폭력예방교육"
    macro(lecture_name, args.id, args.pw)
