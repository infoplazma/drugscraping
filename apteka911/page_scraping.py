import os
import re
import time
from typing import Tuple, List
from pprint import pprint
import hashlib
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from settings import APTEKA911
from core.utilities import add_tail


DOMAIN_URL = r"https://apteka911.ua/ua"
SOURCE_HTML_DIR = os.path.join(APTEKA911, "data", "html_source")


def scrape_pages(domain_url: str, source_page_dir: str, drug_list: List[str]) -> List[Tuple[str, str]]:
    """

    :param domain_url:
    :param source_page_dir:
    :param drug_list:  - список препаратов для скрапинга

    return: list of refused_url in format list[(drug, url, message)]
    """

    refused_url: List[Tuple[str, str]] = list()

    if not os.path.isdir(source_page_dir):
        os.makedirs(source_page_dir, exist_ok=True)

    driver = uc.Chrome()
    driver.maximize_window()

    for drug in drug_list:
        print("="*120)
        print(f"Scraping: '{drug}'...\n")
        driver.get(domain_url)
        driver.implicitly_wait(3)

        form_element = driver.find_element(By.ID, 'search')
        # print(formElement.get_attribute("outerHTML"))
        input_element = form_element.find_element(By.XPATH, '//*[@id="search"]')
        input_element.send_keys(drug)
        time.sleep(3)

        button_element = form_element.find_element(By.XPATH, '/html/body/div[1]/header/div[3]/div/div/div/div[3]/form/button')
        # print(button_element)

        button_element.click()
        time.sleep(5)
        window_after = driver.window_handles[-1]
        driver.switch_to.window(window_after)

        if not_found := driver.find_elements(By.XPATH, '//*/section/div/div/h1[@class="mb30"]'):
            # print("Швидкий пошук не дав результатів" in not_found[0].text)
            pprint(not_found[0].text)
            refused_url.append((drug, domain_url, not_found[0].text))
            continue

        # New page
        preparations_elements = driver.find_elements(By.XPATH, "//*/div[@class='block-prod-full extra-small']")
        # print(*preparations_elements, sep="\n")
        a_elements = [element.find_element(By.XPATH, ".//*/p[@class='prod__header']/a") for element in preparations_elements]
        # print(*a_elements, sep="\n")
        urls = [element.get_attribute("href") for element in a_elements if element]
        # print(f"{urls=}", sep="\n")
        # print(f"{driver.current_url=}", sep="\n")

        if not urls and re.search(r"/([\w-]+-d\d+)$", driver.current_url):
            urls = [driver.current_url]

        if not urls:
            pprint("Не найден ни один подходящий url")
            refused_url.append((drug, driver.current_url, "Не найден ни один подходящий url"))
            continue

        for url in urls:
            match = re.search(r"(/([\w-]+-d\d+)$)|(/([\w-]+-p\d+)$)", url)
            if match:
                driver.get(url)
                time.sleep(3)
                driver.implicitly_wait(3)

                if product_name := driver.find_elements(By.XPATH, "//*/div[@class='product-head-instr tl']/h1"):
                    product_name = product_name[0].text
                elif product_name := driver.find_elements(By.XPATH, "//*/section[@class='wrp-content content-right']/h1"):
                    product_name = product_name[0].text
                    # print(f"{product_name=}")
                else:
                    product_name = match.group(1)

                html_content = driver.page_source + add_tail(drug, product_name, url)
                hashed_data = hashlib.md5((drug+product_name+url).encode())
                hashed_filename = hashed_data.hexdigest() + ".html"

                path = os.path.abspath(os.path.join(source_page_dir, hashed_filename))
                with open(path, 'w', encoding="utf-8") as file:
                    file.write(html_content)
                print(f"product_name:'{product_name}'\nurl:'{url}'\nsaved:'{path}'\n")
            else:
                refused_url.append((drug, url, "url не соответствует шаблону"))
                print(f"drug:'{drug}'\nurl:'{url}'\nmessage:'url не соответствует шаблону'\n")
                continue

    driver.quit()
    return refused_url


if __name__ == "__main__":
    import settings
    from apteka911.service_utilities.one_drive_txt_file_to_df import transform_to_df
    from apteka911.data.refused_urls_unused_drugs import PARSING_UNUSED_DRUGS

    # START_DRUG = "Синекод краплі ор. д/діт. 5 мг/мл по 20 мл у флак."

    # df = transform_to_df(settings.ONE_DRIVE_DIR)
    # DRUG_LIST = sorted(df["drug"].unique())
    # index = DRUG_LIST.index(START_DRUG)
    # DRUG_LIST = DRUG_LIST[index:]
    # print(f"{index=}  {DRUG_LIST[0]=}")

    # SOURCE_HTML_DIR = "./data/html_source_test"
    # DRUG_LIST = ["Азитро Сандоз пор. д/п сусп",
    #              # "Окомістин  - розчин",
    #              # "Цедоксим порошок для оральної суспензії 40 мг/5 мл флакон 100 мл 1 шт",
    #              # "Цефодокс таблетки вкриті плівковою оболонкою по 100 мг блістер 10 шт",
    #     # 'Суспрін розчин д/ор. заст. 4 мг/5 мл по 50 мл у флак', "Ефералган для дітей"
    #              ]
    DRUG_LIST = PARSING_UNUSED_DRUGS

    # print(*drug_list, sep="\n")
    print(f"{len(DRUG_LIST)=}")

    print("SCRAPING:")
    refused_url_ = scrape_pages(DOMAIN_URL, SOURCE_HTML_DIR, DRUG_LIST)
    print("="*120)

    print("REFUSED URLS:")
    pprint(refused_url_)
