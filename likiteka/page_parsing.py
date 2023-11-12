"""
Парсинг html файлов дял домена likiteka
"""
import os
import re
from typing import Tuple, List
from collections import namedtuple

from settings import CUSTOM_DRUG_TAG, CUSTOM_URL_TAG, SIMPLY_RELEASE_FORM_COLUMN, COMPOSITION_COLUMN, TRADE_NAME_COLUMN
from settings import DRUG_COLUMN, PRODUCT_NAME_COLUMN, RELEASE_FORM_COLUMN, SYMPTOM_COLUMN
from settings import ACTIVE_INGREDIENTS_COLUMN, CHILDREN_COLUMN, URL_COLUMN

import codecs
import numpy as np
import pandas as pd
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
        list of refused_url in format list[(drug, url)]
    """

    refused_url: List[Tuple[str, str]] = list()

    record_list: List[dict] = list()
    for root, _, dir_files in os.walk(source_page_dir):
        # print(f"{root=}")
        for file in tqdm(dir_files, desc='Parsing html files', ncols=100, disable=disable_tqdm):
            if not str(file).startswith("~$") and (str(file).endswith(".html") or str(file).endswith(".txt")):

                path = os.path.abspath(os.path.join(root, file))
                file_obj = codecs.open(path, encoding="utf-8")
                page_source = file_obj.read()
                file_obj.close()

                soup = BeautifulSoup(page_source, 'html5lib')
                drug = soup.find(CUSTOM_DRUG_TAG).text
                if drug not in drug_list:
                    continue

                chapters = soup.findAll('div', attrs={'class': 'tablets-tabs__item tablets-tabs__item_active'})
                if chapters is None:
                    refused_url.append((drug, url))
                    continue

                url = soup.find(CUSTOM_URL_TAG).text

                # product_name
                product_name = soup.find('div', attrs={'class': 'tablets-container'}).find('h1').text

                # Форма выпуска
                try:
                    release_form = soup.find('p', string="Лікарська форма").find_next('p').text
                except AttributeError:
                    refused_url.append((drug, url, 'Лікарська форма', 'AttributeError'))
                    release_form = np.nan

                # Діюча речовина
                pattern = r"діюч[аі]+[\&nbsp\;\s]+речовин[аи]+"
                active_ingredients = np.nan
                for tag in ['i', 'em']:
                    try:
                        element = soup.find(tag, string=re.compile(pattern, flags=re.I))
                        active_ingredients = element.parent.text.replace('\xa0', '')
                        break
                    except AttributeError:
                        pass

                if active_ingredients is np.nan:
                    for tag in ['p']:
                        try:
                            active_ingredients = soup.find(tag, string=re.compile(pattern, flags=re.I)).text.replace('\xa0', '')
                            break
                        except AttributeError:
                            pass

                if active_ingredients is np.nan:
                    refused_url.append((drug, url, 'Діюча речовина', 'AttributeError'))

                # Заполняем словарь
                record = {DRUG_COLUMN: drug,
                          PRODUCT_NAME_COLUMN: product_name,
                          TRADE_NAME_COLUMN: product_name,
                          ACTIVE_INGREDIENTS_COLUMN: active_ingredients,
                          SIMPLY_RELEASE_FORM_COLUMN: release_form,
                          RELEASE_FORM_COLUMN: release_form,
                          COMPOSITION_COLUMN: np.nan,
                          CHILDREN_COLUMN: np.nan,
                          URL_COLUMN: url}

                record.update({item.header: item.content for item in _parse_page(chapters)})
                record_list.append(record)

    df = pd.DataFrame(record_list)
    return df, refused_url


def _parse_page(chapters: bs4.element.ResultSet) -> List[DataPage]:
    data_list: List[DataPage] = list()
    for chapter in chapters:
        header = _format_text(chapter.find_next('h2').text.replace(chapter.find_next('span').text, ''))
        content = _format_text(chapter.find_next('div', attrs={'class': 'tablets-tabs__box'}).text)
        data_list.append(DataPage(header, content))

    return data_list


def set_symptom(df_source: pd.DataFrame, df_target: pd.DataFrame, desc_tqdm='Index', disable_tqdm=False) -> pd.DataFrame:
    for index_src in tqdm(df_source.index, desc=desc_tqdm, ncols=100, disable=disable_tqdm):
        value = df_source.loc[index_src, DRUG_COLUMN]
        if value is not np.nan:
            idx = df_target[df_target[DRUG_COLUMN] == value].index
            if idx.values.size:
                df_target.loc[idx, SYMPTOM_COLUMN] = df_source.loc[index_src, SYMPTOM_COLUMN]

    return df_target


def _format_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
