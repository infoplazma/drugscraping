"""
Логирует названия форм выпуска препарата из задания и из соскрепленных данных с сайтов, и сохраняет в двух файлах
в каталоге ./data
"""
import os
import re
from typing import List

import pandas as pd

import settings as stt
from core.utilities import read_log, save_lines
from core.excel_maker import ExcelMaker


def reload_release_form_files(maker: ExcelMaker, df_parsed: pd.DataFrame):
    """
    Создает и обновляет файлы с перечнем форм выпуска препаратов.

    :param maker - объект с данными по заданию
    :param df_parsed - объект с распарсенными данными с сайтов
    """

    _reload(stt.RELEASE_FORM_TASK_PATH, maker.release_form_list)
    parsed_release_form_list = df_parsed[stt.RELEASE_FORM_COLUMN].unique().tolist()
    _reload(stt.RELEASE_FORM_PARSED_PATH, parsed_release_form_list)


def _reload(path: str, release_form_list: List[str]):

    release_form_list = list(
        map(lambda x: re.sub(r"\s+", " ", x).replace("\xa0", " ").strip(), release_form_list))

    if os.path.isfile(path):
        prev_release_form_list = read_log(path)
        if set(release_form_list).difference(set(prev_release_form_list)):
            release_form_list = sorted(set(prev_release_form_list + release_form_list))
            save_lines(path, release_form_list)
            print(f"Обновлены данные с перечнем форм выпуска препаратов:'{path}'")
    else:
        save_lines(path, sorted(release_form_list))
        print(f"Сохранены данные с перечнем форм выпуска препаратов:'{path}'")
