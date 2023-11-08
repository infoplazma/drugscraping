from typing import List, Dict
import pandas as pd
from icecream import ic

import settings as stt
from core.utilities import DFS_TYPE, check_column_names_in_df
from core.utilities import read_excel_package, reset_column_positions


class ExcelMaker:
    """
    Класс для создания файла для загрузки в базу
    """

    def __init__(self):
        self.scheme: DFS_TYPE = None
        self.drug_list: List[str] = None
        self.release_form_list: List[str] = None

    def make(self, drug_task_path: str, parsed_frame: pd.DataFrame) -> pd.DataFrame:
        """
        Создает конечный файл со схемой лечения для препаратов из файла drug_task_path

        :param drug_task_path: - путь к текстовому файлу где построчно указаны названия препаратов
        :param parsed_frame: - распарсенные данные
        :return: схему лечения в формате DataFrame
        """
        custom_scheme: DFS_TYPE = dict()
        for sheet_name, df in self.scheme.items():
            rows = list()
            for index, row in df.iterrows():
                ...

    def prepare_scheme(self, scheme_dir_path: str, columns: Dict[str, str] = None) -> pd.DataFrame:
        """
        Подготавливает развернутую совокупную таблицу схемы лечения со всех excel файлов из общего каталога.

        :param scheme_dir_path: путь к директории где находятся файлы с заданными схемами лечения
        :param columns: словарь для переименования имен колонок
        :return: схему лечения в формате DataFrame из модуля page_parsing
        """
        self.scheme: DFS_TYPE = dict()
        self.drug_list: List[str] = list()
        self.release_form_list: List[str] = list()
        dfs = read_excel_package(scheme_dir_path)

        for sheet_name, df in dfs.items():
            print(f"{sheet_name}...")
            if columns:
                df = df.rename(columns=columns)

            df = self._prepare_df(df)
            self.scheme[sheet_name] = df
            self.drug_list.extend(df[stt.DRUG_COLUMN].values)
            self.release_form_list.extend(df[stt.RELEASE_FORM_COLUMN].values)

        self.drug_list = list(sorted(set(self.drug_list)))
        self.release_form_list = list(sorted(set(self.release_form_list)))
        if '' in self.drug_list:
            self.drug_list.remove('')
        if '' in self.release_form_list:
            self.release_form_list.remove('')

    @staticmethod
    def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
        """
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


