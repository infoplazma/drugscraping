import os
import re
import time
from typing import Tuple, List
import hashlib
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from core.utilities import add_tail


def scrape_pages(domain_url: str, source_page_dir: str, drug_list: List[str]) -> List[Tuple[str, str]]:
    """

    :param domain_url:
    :type domain_url:
    :param source_page_dir:
    :type source_page_dir:
    :param drug_list:  - список препаратов для скрапинга

    return: list of refused_url in format list[(drug, url)]
    """

    refused_url: List[Tuple[str, str]] = list()

    if not os.path.isdir(source_page_dir):
        os.mkdir(source_page_dir)

    driver = uc.Chrome()
    driver.maximize_window()

    for drug in drug_list:
        print(f"\nScraping {drug}...")
        driver.get(domain_url)
        driver.implicitly_wait(3)

        form_element = driver.find_element(By.ID, 'search')
        # print(formElement.get_attribute("outerHTML"))
        input_element = form_element.find_element(By.CLASS_NAME, 'search-box__input')
        input_element.send_keys(drug)
        time.sleep(3)

        button_element = form_element.find_element(By.CLASS_NAME, 'search-box__btn')
        # print(buttonElement)

        button_element.click()
        time.sleep(5)
        window_after = driver.window_handles[-1]
        driver.switch_to.window(window_after)

        # New page
        preparations_elements = driver.find_elements(By.XPATH, "//a[@class='preparations-item']")
        urls = [element.get_attribute('href') for element in preparations_elements]

        for url in urls:
            match = re.search(r"/([\w-]+)/$", url)
            if match:
                product_name = match.group(1)
                driver.get(url)
                driver.implicitly_wait(3)

                html_content = driver.page_source + add_tail(drug, product_name, url)
                hashed_data = hashlib.sha1(html_content.encode())
                hashed_filename = hashed_data.hexdigest() + ".html"

                path = os.path.abspath(os.path.join(source_page_dir, hashed_filename))
                with open(path, 'w', encoding="utf-8") as file:
                    file.write(html_content)
                print(f"'{product_name}' saved: '{url}'")
            else:
                refused_url.append((drug, url))
                print(f"not found pattern for {url=}")

    driver.quit()
    return refused_url


if __name__ == "__main__":
    from icecream import ic
    from settings import DOMAINS, TASK_FILE_PATH
    from core.utilities import read_log

    DRUG_LIST = read_log(TASK_FILE_PATH)
    ic(DRUG_LIST)

    # scrape_pages(domain_url=LIKITEKA_DOMAIN, source_page_dir=LIKITEKA_SOURCE_DIR, drug_list=DRUG_LIST)

