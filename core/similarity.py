"""
Оценка схожести выражений на основе пакета spacy
"""
import os
import re
from typing import Tuple, List, Literal

from tqdm import tqdm

import spacy

from core.utilities import LOG_SEP, parse_log_lines, read_log

# from icecream import ic

# ic.configureOutput(includeContext=True)

DESCRIPTION = """# Не определяемые выражения для форм выпуска препаратов в модели nlp пакета spacy-ru.
# Разделитель " | "
# Структура:
#   Первое значение - оригинал выражения, не редактируемое, справочно.
#   Второе значение - очищенная копия оригинала выражения, не редактируемое, справочно.
#   Третье значение - regex pattern для очищенной копии выражения (Второе значение), значение редактируемое.
#   Четвертое значение - заменитель, значение редактируемое.
# 
"""


class Substitution:
    """
    Класс производит подстановку не найденных выражений в модели spacy
    """
    def __init__(self, sub_list: List[Tuple[str, ...]], min_len=4):

        self.sub_list = [item for item in sub_list if len(item) >= min_len]
        self.sub_list = sorted(self.sub_list, key=lambda item: item[1], reverse=True)

        self.origin_list = [item[0] for item in self.sub_list]
        self.cln_list = [item[1] for item in self.sub_list]
        self.pattern_list = [item[2].strip() for item in self.sub_list]
        self.replacement_list = [item[3] for item in self.sub_list]

    def __call__(self, string: str, *args, **kwargs) -> str:
        found = map(lambda p: p if bool(re.search(p, cleanup(string), flags=re.I)) else None, self.pattern_list)
        if patterns := tuple(filter(lambda item: item is not None, found)):
            index = self.pattern_list.index(patterns[0])
            return self.replacement_list[index].strip()
        return string


def save_unrecognizable(path: str,
                        string_list: List[str],
                        nlp: spacy = None,
                        model: Literal['sm', 'md', 'lg'] = 'lg') -> None:
    """
    Сохраняет в файле выражения форм выпуска препарата которые не распознаются объектом nlp пакета spacy-ru.
    """
    nlp = get_nlp(nlp, model)
    mode = 'w'

    if os.path.isfile(path):
        lines = read_sub_list(path)
        previous_sentence_list = [line[0] for line in lines]
        string_list = list(set(string_list).difference(set(previous_sentence_list)))
        if not string_list:
            print("No new release forms found")
            return

        mode = 'a'

    string_list = sorted(set(string_list))

    _transform: list = lambda l: [l[0], '.*' + l[1].strip() + '.*', l[2]]
    data = [LOG_SEP.join([sentence] + _transform([cleanup(sentence)] * 3)) for sentence in get_unrecognizable(string_list, nlp)]

    if not data:
        print("No new release forms found")
        return

    msg = f"{len(data)} new release forms appended"

    if mode == 'a':
        data = '\n' + '\n'.join(data)
    elif mode == 'w':
        data = DESCRIPTION + '\n'.join(data)

    with open(path, mode, encoding='utf-8') as file:
        file.write(data)

    print(msg)
    print(f"File saved '{os.path.abspath(path)}'")


def get_nlp(nlp: spacy, model: Literal['sm', 'md', 'lg'] = 'lg') -> spacy:
    if nlp is None:
        model_error(model)
        print(f"Loading nlp model...")
        nlp = spacy.load(f'ru_core_news_{model}')
    return nlp


def get_unrecognizable(string_list: List[str], nlp: spacy = None, model: Literal['sm', 'md', 'lg'] = 'lg') -> List[str]:
    nlp = get_nlp(nlp, model)
    return sorted(list(set([string for string in tqdm(set(string_list), ncols=100, desc='get_unrecognizable') if not nlp(cleanup(string)).vector.any()])))


def model_error(model: Literal['sm', 'md', 'lg']):
    if model not in ['sm', 'md', 'lg']:
        raise ValueError(f"Invalid value {model=} must be ['sm', 'md', 'lg']")


def cleanup(string: str) -> str:
    string = re.sub(r"[\s\,\.\:\;]+", " ", string)
    string = re.sub(r"[ІіїЇ]", "и", string)
    string = re.sub(r"[Єє]", "е", string)
    regex = re.compile(r"[^A-Za-zА-Яа-я0-9ІіЄєїЇ\s]+", flags=re.I)
    string = regex.sub('', string.lower().strip())
    return string


def read_sub_list(path: str) -> List[Tuple[str, ...]]:
    return parse_log_lines(lines=read_log(path))
