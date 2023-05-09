from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://www.teashop.com/tes-rooibos-e-infusiones/"
PAGE_PARAM = "?page="


def _create_driver():
    driver_path = ChromeDriverManager(path='.').install()
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(driver_path),
                              options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', "
                          "{get: () => undefined})")
    driver.maximize_window()
    return driver


def _get_tea_data(driver):
    teas = []
    tea_index = 0
    while True:
        labels = driver.find_elements(By.CLASS_NAME, 'buyForm')
        if not labels:
            return teas
        label = labels[tea_index]
        label.click()
        # sometimes this element never appears
        # WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
        # (By.CLASS_NAME, "product-review-summary"))).get_attribute("value")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        name = soup.find("h1").contents[0]
        tags = [tag.contents[0].strip()
                for tag in soup.find_all("div", {"class": "ct-function"})]
        # commented due to occasionally disappearing ratings
        # reviews_count = int(soup.find("span",
        # {"class": "ts-stars-reviewCount"}).contents[0][1:-1])
        # removes parenthesis
        # rating = float(soup.find("span", {"class":
        # "ts-reviewSummary-ratingValue"}).contents[0])
        description = soup.find("div", {"class": "product-long-description"}
                                ).get_text().strip().replace("\xa0", " ")
        titles = (title.contents[0]
                  for title in soup.find_all(
            "div", {"class": "title-characteristics"}))
        values = (title.contents[0].get_text()
                  for title in soup.find_all(
            "div", {"class": "text-characteristics"}))
        characteristics = dict(zip(titles, values))
        price = float(soup.find("meta", {"itemprop": "price"}
                                ).attrs['content'])
        tea = dict(name=name,
                   tags=tags,
                   # reviews_count=reviews_count,
                   # rating=rating,
                   description=description,
                   characteristics=characteristics,
                   price=price)
        teas.append(tea)
        print(name)
        driver.back()
        tea_index += 1
        if len(labels) == tea_index:
            break
    return teas


def fetch_teas():
    teas = []
    driver = _create_driver()
    page_number = 1
    while True:
        url = URL + PAGE_PARAM + str(page_number)
        driver.get(url)
        teas_on_page = _get_tea_data(driver)
        if len(teas_on_page) == 0:
            break
        teas.extend(teas_on_page)
        page_number += 1
    driver.quit()
