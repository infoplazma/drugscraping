"""
Парсинг html файлов дял домена likiteka
"""
import os
from typing import Tuple, List, Dict

from settings import APTEKA911, CUSTOM_DRUG_TAG, CUSTOM_URL_TAG, CUSTOM_PRODUCT_NAME_TAG

import codecs
import pandas as pd
from lxml import etree
from bs4 import BeautifulSoup

from tqdm import tqdm

SOURCE_HTML_DIR = os.path.join(APTEKA911, "data", "html_source")
PARSED_DATA_PATH = os.path.join(APTEKA911, "data", "parsed_data.csv")


def parse_pages(source_page_dir: str, drug_list: List[str], disable_tqdm=False) -> Tuple[
                                                                pd.DataFrame, List[Tuple[str, str, str]], List[str]
]:

    """

    :param source_page_dir:
    :param drug_list: список препаратов для парсинга
    :param disable_tqdm:

    return: two tuple with two parameters:
        pd.DataFrame
        list of refused_url in format list[(drug, url, message)]
    """

    refused_url: List[Tuple[str, str]] = list()
    unused_drugs = list(drug_list)

    i = 0
    record_list: List[dict] = list()
    for root, _, dir_files in os.walk(source_page_dir):
        n = len(dir_files)
        for file in tqdm(dir_files, desc='Parsing html files', ncols=100, disable=disable_tqdm):
            if not str(file).startswith("~$") and (str(file).endswith(".html")):
                i += 1
                path = os.path.abspath(os.path.join(root, file))
                file_obj = codecs.open(path, encoding="utf-8")
                page_source = file_obj.read()
                file_obj.close()

                soup = BeautifulSoup(page_source, 'html5lib')
                dom = etree.HTML(str(soup))

                drug = soup.find(CUSTOM_DRUG_TAG).text
                product_name = soup.find(CUSTOM_PRODUCT_NAME_TAG).text
                url = soup.find(CUSTOM_URL_TAG).text

                if drug not in drug_list:
                    if disable_tqdm:
                        print(f"'{drug}' не найден в drug_list")
                    continue

                if drug in unused_drugs:
                    unused_drugs.remove(drug)

                if disable_tqdm:
                    print("="*120)
                    print(f"[{i}==>{n}] Parsing product_name:'{product_name}'...\nurl:'{url}'\n")

                text = ''
                for use_method in ["Особливості застосування", "Спосіб застосування", "Застосування", "Рекомендації щодо застосування", "Спосіб застосування та дози"]:
                    if h1_header := dom.xpath(f'//*/div[@class="collapsible-heading open-block"]/h2[contains(text(), "{use_method}")]'):
                        # print(f"\n{h1_header[0].text}:")
                        parent = h1_header[0].xpath('../following-sibling::div')
                        text += h1_header[0].text + ': ' + ' '.join(parent[0].itertext()).strip() + "\r\n\n"

                if not text:
                    if disable_tqdm:
                        print(f"not found in url:'{url}'\n")
                    refused_url.append((drug, url, "Не найдено 'Особливості застосування' или 'Спосіб застосування' или 'Застосування' или 'Рекомендації щодо застосування' или 'Спосіб застосування та дози'"))
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
    return df, refused_url, unused_drugs


if __name__ == "__main__":
    from pprint import pprint
    import settings
    from apteka911.service_utilities.one_drive_txt_file_to_df import transform_to_df

    df_ = transform_to_df(settings.ONE_DRIVE_DIR)
    DRUG_LIST = sorted(df_["drug"].unique())

    # DRUG_LIST = ["Преднізолон-Дарниця таблетки по 5 мг №40 (10х4)", "Назірус Синус капсули по 370 мг №30 (10х3)"]
    # print(*drug_list, sep="\n")
    print(f"{len(DRUG_LIST)=}")

    df_, refused_url_, unused_drugs_ = parse_pages(SOURCE_HTML_DIR, DRUG_LIST)
    df_.to_csv(PARSED_DATA_PATH, index=False)
    # print("Refused urls:")
    # pprint(df_.to_dict())
    # print("="*120)

    print("Refused urls:")
    pprint(refused_url_)
    print("=" * 120)

    print("Unused drugs:")
    pprint(unused_drugs_)

"""
"""
