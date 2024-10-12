from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class WebDriverManager:
    def __init__(self, download_path):
        self.download_path = download_path

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-sha-usage")

        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(1)
        return driver
