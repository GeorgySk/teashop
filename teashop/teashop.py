import time
from concurrent.futures import ThreadPoolExecutor
from typing import (Dict,
                    List)

import requests
from bs4 import (BeautifulSoup,
                 Tag)
from yarl import URL

PRODUCTS_URL = URL("https://www.teashop.com/tes-rooibos-e-infusiones")
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


def fetch_teas(*,
               max_workers: int = 10,
               sleep_time: float = 1):
    products_page_soup = _get_soup(PRODUCTS_URL)
    pages_count = _get_pages_count(products_page_soup)
    pages_numbers = range(1, pages_count + 1)
    pages_urls = (PRODUCTS_URL.with_query(page=page) for page in pages_numbers)
    pages_soups = map(_get_soup, pages_urls)
    forms_per_page = (page_soup.find_all('form', class_='buyForm')
                      for page_soup in pages_soups)

    tea_urls = []
    for i, forms in enumerate(forms_per_page, start=1):
        print(f"Page: {i}")
        tea_urls.extend(map(_tea_url_from_form, forms))

    tea_info_list = []
    with ThreadPoolExecutor(max_workers) as executor:
        total_teas = len(tea_urls)
        for i, tea_info in enumerate(executor.map(get_tea_info, tea_urls)):
            print(f"Processed {i}/{total_teas} teas")
            tea_info_list.append(tea_info)
            time.sleep(sleep_time)

    return tea_info_list


def _get_soup(url: URL) -> BeautifulSoup:
    html = requests.get(url, headers=HEADERS).text
    return BeautifulSoup(html, 'html.parser')


def _get_pages_count(soup: BeautifulSoup) -> int:
    # pages are written as: 1 2 3 4 ... 10 >>
    return int(soup.find(class_="pagination").find_all('a')[-2].get_text())


def _tea_url_from_form(form: Tag) -> URL:
    path = form.find('a', class_='product-list-info').get('href').strip()
    return URL(PRODUCTS_URL.origin()).with_path(path)


def get_tea_info(tea_url: URL) -> dict:
    soup = _get_soup(tea_url)
    return {'name': _extract_name(soup),
            'description': _extract_description(soup),
            'tags': _extract_tags(soup),
            'characteristics': _extract_characteristics(soup),
            'price': _extract_price(soup),
            'extra_tags': _extract_extra_tags(soup)}


def _extract_name(soup: BeautifulSoup) -> str:
    return soup.find('h1', class_='product-h1').get_text()


def _extract_description(soup: BeautifulSoup) -> str:
    return soup.find('div', class_='product-long-description'
                     ).get_text().strip('\n')


def _extract_tags(soup: BeautifulSoup) -> List[str]:
    return [tag.get_text().strip()
            for tag in soup.find_all('div', class_='ct-function')]


def _extract_characteristics(soup: BeautifulSoup) -> Dict[str, str]:
    characteristics_dict = {}
    characteristics = soup.find_all('div', class_='container-characteristics')
    for characteristic in characteristics:
        title = characteristic.find('div', class_='title-characteristics'
                                    ).get_text()
        text = characteristic.find('div', class_='text-characteristics'
                                   ).get_text()
        characteristics_dict[title] = text
    return characteristics_dict


def _extract_price(soup: BeautifulSoup) -> str:
    return soup.find('span', class_='product-price'
                     ).find('meta').get('content')


def _extract_extra_tags(soup: BeautifulSoup) -> List[str]:
    return [tag.get_text().strip()
            for tag in soup.find_all('div', class_='text-extra-info')]
