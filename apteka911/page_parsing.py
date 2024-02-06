"""
Парсинг html файлов дял домена likiteka
"""
import os
import re
from typing import Tuple, List, Dict
from collections import namedtuple

from settings import CUSTOM_DRUG_TAG, CUSTOM_URL_TAG, CUSTOM_PRODUCT_NAME_TAG

import codecs
import pandas as pd
from lxml import etree
import bs4
from bs4 import BeautifulSoup

from tqdm import tqdm


DataPage = namedtuple('DataPage', ['header', 'content'])


def parse_pages(source_page_dir: str, drug_list: List[str], disable_tqdm=False) -> Tuple[pd.DataFrame, List[Tuple[str, str]]]:
    """

    :param source_page_dir:
    :param drug_list: список препаратов для парсинга
    :param disable_tqdm:

    return: two tuple with two parameters:
        pd.DataFrame
        list of refused_url in format list[(drug, url, message)]
    """

    refused_url: List[Tuple[str, str]] = list()

    record_list: List[dict] = list()
    for root, _, dir_files in os.walk(source_page_dir):
        for file in tqdm(dir_files, desc='Parsing html files', ncols=100, disable=disable_tqdm):
            if not str(file).startswith("~$") and (str(file).endswith(".html")):

                path = os.path.abspath(os.path.join(root, file))
                file_obj = codecs.open(path, encoding="utf-8")
                page_source = file_obj.read()
                file_obj.close()

                soup = BeautifulSoup(page_source, 'html5lib')
                dom = etree.HTML(str(soup))

                drug = soup.find(CUSTOM_DRUG_TAG).text
                product_name = soup.find(CUSTOM_PRODUCT_NAME_TAG).text
                url = soup.find(CUSTOM_URL_TAG).text

                if disable_tqdm:
                    print("="*120)
                    print(f"Parsing product_name:'{product_name}'...\nurl:'{url}'\n")
                if drug not in drug_list:
                    continue

                text = ''
                # "Особливості застосування
                if h1_header := dom.xpath('//*/div[@class="collapsible-heading open-block"]/h2[contains(text(), "Особливості застосування")]'):
                    # print(f"\n{h1_header[0].text}:")
                    parent = h1_header[0].xpath('../following-sibling::div')
                    text += h1_header[0].text + ': ' + ' '.join(parent[0].itertext()).strip() + "\r\n\n"

                if h1_header := dom.xpath('//*/div[@class="collapsible-heading open-block"]/h2[contains(text(), "Спосіб застосування")]'):
                    # print(f"\n{h1_header[0].text}:")
                    parent = h1_header[0].xpath('../following-sibling::div')
                    text += h1_header[0].text + ': ' + ' '.join(parent[0].itertext()).strip()

                if not text:
                    if disable_tqdm:
                        print(f"not found in url:'{url}'\n")
                    refused_url.append((drug, url, "Не найдено 'Особливості застосування' или 'Спосіб застосування'"))
                    continue

                if for_children_div := dom.xpath('//*/div[@class="block-lights__title"][contains(text(), "Дітям")]/following-sibling::div'):
                    text = "Дітям:" + for_children_div[0].text + "\r\n" + text

                # print(text, "\n")
                record = {"drug": drug, "product_name": product_name, "text": text, "url": url}

                if parameter_table := soup.find('table', attrs={'class': 'product-parameters product-parameters--card'}):
                    df_parameters = pd.read_html(str(parameter_table))
                    parameters: Dict[str, str] = {param[0]: param[1] for param in df_parameters[0].values.tolist()}
                    record.update(parameters)
                    # print(f"{parameters}\n")

                record_list.append(record)
                if disable_tqdm:
                    print(f"\tsuccessfully")

    df = pd.DataFrame(record_list)
    return df, refused_url


def _parse_page(chapters: bs4.element.ResultSet) -> List[DataPage]:
    data_list: List[DataPage] = list()
    for chapter in chapters:
        header = _format_text(chapter.find_next('h2').text.replace(chapter.find_next('span').text, ''))
        content = _format_text(chapter.find_next('div', attrs={'class': 'tablets-tabs__box'}).text)
        data_list.append(DataPage(header, content))

    return data_list


def _format_text(text: str) -> str:
    if isinstance(text, str):
        text = re.sub(r'\s+', ' ', text)
        text = text.replace("\xa0", " ").strip()
    return text


if __name__ == "__main__":
    from pprint import pprint
    import settings
    from data_preparing.excel_transformer import transform_to_df

    SOURCE_HTML_DIR = "./html_source"
    df_ = transform_to_df(settings.ONE_DRIVE_DIR)
    DRUG_LIST = sorted(df_["drug"].unique())
    # print(*drug_list, sep="\n")
    print(f"{len(DRUG_LIST)=}")

    df_, refused_url_ = parse_pages(SOURCE_HTML_DIR, DRUG_LIST, True)
    pprint(df_.to_dict())
