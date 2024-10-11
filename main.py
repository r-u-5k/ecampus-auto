from selenium.common.exceptions import TimeoutException, NoSuchElementException
from web_driver_manager import WebDriverManager
from ecampus_automation import ECampusAutomation
import params as pa


def main():
    driver_manager = WebDriverManager(pa.CHROME_DRIVER_PATH)
    driver = driver_manager.get_driver()

    try:
        automation = ECampusAutomation(driver)
        automation.login(pa.userid, pa.password)

        lecture_name = "기업직무분석"
        automation.watch_specific_lecture(lecture_name)

    except TimeoutException:
        print("시간 초과")
    except NoSuchElementException:
        print("해당 요소가 없음")
    except Exception as e:
        print(f"에러 발생: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
