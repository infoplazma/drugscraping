from typing import Tuple, List, Dict, Literal

import pandas as pd
import spacy

# from icecream import ic

import settings as stt
from core.utilities import DFS_TYPE, check_column_names_in_df
from core.similarity import cleanup, get_nlp, get_unrecognizable, Substitution
from core.utilities import read_excel_package


# ic.configureOutput(includeContext=True)


class ExcelMaker:
    """
    Класс для создания файла для загрузки в базу
    """

    def __init__(self, nlp: spacy, substitution: Substitution = None):
        self._nlp = nlp
        self._substitution = substitution

        self._scheme_task: DFS_TYPE = None
        self.drug_list: List[str] = None
        self.release_form_list: List[str] = None

    def make(self, df_parsed: pd.DataFrame, threshold: float = 0.5) -> Tuple[DFS_TYPE, List[Tuple[str, ...]]]:
        """
        Создает конечный файл со схемой лечения для препаратов из файла drug_task_path

        :param df_parsed: таблица с распарсенными данными из соскрепленных html файлов
        :param threshold: порог фильтрации 0..1

        :return: схему лечения в формате кортежа из двух параметров DataFrame и refused
        """
        self._check_load()
        custom_scheme: DFS_TYPE = dict()
        refused: List[Tuple[str, str]] = list()

        # Замена не найденных выражений формы выпуска препаратов на подходящие для модели self.nlp
        if self._substitution:
            df_parsed = self._substitute(df_parsed)

        # remove nan values
        df_parsed.dropna(subset=[stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN], inplace=True)

        count = 1
        for sheet_name, df_task in self._scheme_task.items():
            print(f"{sheet_name} ===> {round(count / len(self._scheme_task) * 100, 2)} %")
            count += 1

            # Замена не найденных выражений формы выпуска препаратов на подходящие для модели self.nlp
            if self._substitution:
                df_task = self._substitute(df_task)

            rows = list()
            for index_parsed, row_parsed in df_parsed.iterrows():
                for index_task, row_task in df_task.iterrows():

                    if row_parsed[stt.DRUG_COLUMN] == row_task[stt.DRUG_COLUMN]:

                        if stt.DEBUG:
                            is_similarity = True
                        else:
                            doc1 = self._nlp(cleanup(row_task[stt.RELEASE_FORM_COLUMN]))
                            doc2 = self._nlp(cleanup(row_parsed[stt.RELEASE_FORM_COLUMN]))
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

                        elif is_all_zeros1 or is_all_zeros2:
                            refused.append((row_parsed[stt.DRUG_COLUMN],
                                            not is_all_zeros1,
                                            row_task[stt.RELEASE_FORM_COLUMN].replace('\xa0', ' '),
                                            not is_all_zeros2,
                                            row_parsed[stt.RELEASE_FORM_COLUMN].replace('\xa0', ' '),
                                            round(similarity, 3),
                                            row_parsed[stt.URL_COLUMN]))

            custom_scheme[sheet_name] = pd.DataFrame(rows)

        return custom_scheme, refused

    def check_model(self, df_parsed: pd.DataFrame) -> Tuple[List[str], bool]:
        """
        Проверяет какие выражения форм выпуска препарата модель не знает, и возвращает их список.

        :param df_parsed: таблица с распарсенными данными из соскрепленных html файлов

        :return Список форм выпуска препаратов не распознаваемые spacy-ru и режим редактирования в булевом значении,
        указывающий редактировать или нет файл содержащий список подстановок sub_list
        """
        self._check_load()

        joint_release_form_list = set(df_parsed[stt.RELEASE_FORM_COLUMN].unique().tolist() + self.release_form_list)

        if self._substitution:
            joint_release_form_list = [self._substitution(release_form) for release_form in joint_release_form_list]

        return get_unrecognizable(joint_release_form_list,
                                  self._nlp,
                                  desc="проверка всех форм выпуска на распознавание")

    def set_substitution(self, substitution: Substitution):
        self._substitution = substitution

    def load(self, task_config_dir_path: str, columns: Dict[str, str] = None):
        """
        Загружает и подготавливает развернутую совокупную таблицу задания схемы лечения со всех excel
        файлов из каталога tasks.
        По сути выполняет инициализацию основных атрибутов класса.

        :param task_config_dir_path: путь к директории где находятся файлы с заданными схемами лечения
        :param columns: словарь для переименования имен колонок
        """
        self._scheme_task: DFS_TYPE = dict()
        self.drug_list: List[str] = list()
        self.release_form_list: List[str] = list()

        dfs = read_excel_package(task_config_dir_path)

        count = 1
        for sheet_name, df in dfs.items():
            print(f"{sheet_name} ===> {round(count/len(dfs)*100, 2)} %")
            count += 1

            # Переименование колонок
            if columns:
                df = df.rename(columns=columns)

            df = self._prepare_df_task(df)
            self._scheme_task[sheet_name] = df
            self.drug_list.extend(df[stt.DRUG_COLUMN].values.tolist())
            self.release_form_list.extend(df[stt.RELEASE_FORM_COLUMN].values.tolist())

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

    def _substitute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Выполняет замену в таблице DataFrame
        """
        release_form_list = df[stt.RELEASE_FORM_COLUMN].unique().tolist()
        for release_form in release_form_list:
            df[stt.RELEASE_FORM_COLUMN] = df[stt.RELEASE_FORM_COLUMN].replace(regex=release_form,
                                                                              value=self._substitution(release_form))
        return df

    def _check_load(self):
        if self._scheme_task is None or self.drug_list is None or self.release_form_list is None:
            raise ValueError("Any attributes are missing, make sure you have previously run the method 'load'.")
