from typing import Tuple, List, Dict, Literal

import numpy as np
import pandas as pd

# from icecream import ic

import settings as stt
from core.utilities import DFS_TYPE, check_column_names_in_df
from core.similarity import cleanup
from core.utilities import read_excel_package

if not stt.DEBUG:
    import spacy

# ic.configureOutput(includeContext=True)


class ExcelMaker:
    """
    Класс для создания файла для загрузки в базу
    """

    def __init__(self):
        self.scheme_task: DFS_TYPE = None
        self.drug_list: List[str] = None
        self.release_form_list: List[str] = None

    def make(self, drug_task_list: List[str],
             df_parsed: pd.DataFrame,
             threshold: float = 0.5,
             model: Literal['sm', 'md', 'lg'] = 'lg') -> Tuple[DFS_TYPE, List[Tuple[str, ...]]]:
        """
        Создает конечный файл со схемой лечения для препаратов из файла drug_task_path

        :param drug_task_list: - список препаратов
        :param df_parsed: - таблица с распарсенными данными из html файлов
        :param threshold: порог фильтрации
        :param model: какую лингвинистическую модель использовать

        :return: схему лечения в формате кортежа из двух параметров DataFrame и refused
        """
        if model not in ['sm', 'md', 'lg']:
            raise ValueError(f"Invalid value {model=} must be ['sm', 'md', 'lg']")

        if not stt.DEBUG:
            nlp = spacy.load(f'ru_core_news_{model}')

        custom_scheme: DFS_TYPE = dict()
        refused: List[Tuple[str, str]] = list()

        # remove nan values
        df_parsed.dropna(subset=[stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN], inplace=True)

        count = 1
        for sheet_name, df_task in self.scheme_task.items():
            print(f"{sheet_name} ===> {round(count/len(self.scheme_task)*100, 2)} %")
            count += 1

            rows = list()
            for index_parsed, row_parsed in df_parsed.iterrows():
                for index_task, row_task in df_task.iterrows():

                    if row_parsed[stt.DRUG_COLUMN] == row_task[stt.DRUG_COLUMN] and row_parsed[stt.DRUG_COLUMN] in drug_task_list:

                        if stt.DEBUG:
                            is_similarity = True
                        else:
                            doc1 = nlp(cleanup(row_task[stt.RELEASE_FORM_COLUMN]))
                            doc2 = nlp(cleanup(row_parsed[stt.RELEASE_FORM_COLUMN]))
                            is_all_zeros1 = not doc1.vector.any()
                            is_all_zeros2 = not doc2.vector.any()

                            if is_all_zeros1 or is_all_zeros2:
                                similarity = 0
                            else:
                                similarity = doc1.similarity(doc2)

                            is_similarity = similarity >= threshold

                        if is_similarity:
                            row = {stt.ORDER_COLUMN: row_task[stt.ORDER_COLUMN],
                                   stt.SYMPTOM_COLUMN: row_task[stt.SYMPTOM_COLUMN]}
                            row.update(dict(row_parsed))
                            row[stt.SIMPLY_RELEASE_FORM_COLUMN] = row_task[stt.RELEASE_FORM_COLUMN]
                            rows.append(row)
                        else:
                            refused.append((row_parsed[stt.DRUG_COLUMN],
                                            not is_all_zeros1,
                                            row_task[stt.RELEASE_FORM_COLUMN].replace('\xa0', ' '),
                                            not is_all_zeros2,
                                            row_parsed[stt.RELEASE_FORM_COLUMN].replace('\xa0', ' '),
                                            round(similarity, 3),
                                            row_parsed[stt.URL_COLUMN]))

            custom_scheme[sheet_name] = pd.DataFrame(rows)

        return custom_scheme, refused

    def load(self, task_dir_path: str, columns: Dict[str, str] = None):
        """
        Загружает и подготавливает развернутую совокупную таблицу задания схемы лечения со всех excel
        файлов из общего каталога.

        :param task_dir_path: путь к директории где находятся файлы с заданными схемами лечения
        :param columns: словарь для переименования имен колонок
        """
        self.scheme_task: DFS_TYPE = dict()
        self.drug_list: List[str] = list()
        self.release_form_list: List[str] = list()

        dfs = read_excel_package(task_dir_path)

        for sheet_name, df in dfs.items():
            print(f"{sheet_name} => ............")
            if columns:
                df = df.rename(columns=columns)

            df = self._prepare_df_task(df)
            self.scheme_task[sheet_name] = df
            self.drug_list.extend(df[stt.DRUG_COLUMN].values)
            self.release_form_list.extend(df[stt.RELEASE_FORM_COLUMN].values)

        self.drug_list = list(sorted(set(self.drug_list)))
        self.release_form_list = list(sorted(set(self.release_form_list)))
        if '' in self.drug_list:
            self.drug_list.remove('')
        if '' in self.release_form_list:
            self.release_form_list.remove('')

    @staticmethod
    def _prepare_df_task(df: pd.DataFrame) -> pd.DataFrame:
        """
        Приводит до ума таблицу с заданием

        :param columns: словарь для переименования имен колонок
        """
        def parse_row_item(text: str) -> List[str]:
            if isinstance(text, str):
                return text.split("//")
            else:
                return [text]

        check_column_names_in_df(df, [stt.SYMPTOM_COLUMN, stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN])

        # remove nan values
        df.dropna(subset=[stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN], inplace=True)

        rows = list()
        for index, row in df.iterrows():
            for symptom in parse_row_item(row[stt.SYMPTOM_COLUMN]):
                for drug in parse_row_item(row[stt.DRUG_COLUMN]):
                    for release_form in parse_row_item(row[stt.RELEASE_FORM_COLUMN]):
                        row_ = {k: v for k, v in dict(row).items() if k not in (stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN, stt.SYMPTOM_COLUMN)}
                        row_[stt.SYMPTOM_COLUMN] = symptom.strip()
                        row_[stt.DRUG_COLUMN] = drug.strip()
                        row_[stt.RELEASE_FORM_COLUMN] = release_form.strip()
                        rows.append(row_)

        return pd.DataFrame(rows)


