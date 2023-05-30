from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import trange
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://www.teashop.com/tes-rooibos-e-infusiones/"
PAGE_PARAM = "?page="


def _create_driver():
    driver_path = ChromeDriverManager(path='.').install()
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(driver_path),
                              options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', "
                          "{get: () => undefined})")
    driver.maximize_window()
    return driver


def _pages_count(driver):
    pagination = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pagination")))
    penultimate_element = pagination.find_elements(By.TAG_NAME, "li")[-2]
    return int(penultimate_element.find_element(By.TAG_NAME, "a").text)


def _get_tea_data(driver):
    teas = []
    labels = driver.find_elements(By.CLASS_NAME, 'buyForm')
    if not labels:
        return teas
    for tea_index in trange(len(labels), desc='Tea on the page', leave=False):
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
        driver.back()
        labels = driver.find_elements(By.CLASS_NAME, 'buyForm')
    return teas


def fetch_teas():
    teas = []
    driver = _create_driver()
    driver.get(URL)
    pages_count = _pages_count(driver)
    for page_number in trange(1, pages_count + 1, desc='Page'):
        url = URL + PAGE_PARAM + str(page_number)
        driver.get(url)
        teas_on_page = _get_tea_data(driver)
        teas.extend(teas_on_page)
    driver.quit()
    return teas
