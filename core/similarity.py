"""
Оценка схожести выражений
"""
import re
from typing import Tuple, List, Literal

import spacy
from tqdm import tqdm
# from icecream import ic

# ic.configureOutput(includeContext=True)


def evaluate_similarity(list1: List[str], list2: List[str],
                        threshold: float = 0.0,
                        model: Literal['sm', 'md', 'lg'] = 'lg') -> List[Tuple[str, str, float]]:

    if not (0 <= threshold <= 1):
        raise ValueError(f"Invalid value {threshold=} must be 0 <= threshold <= 1")

    if model not in ['sm', 'md', 'lg']:
        raise ValueError(f"Invalid value {model=} must be ['sm', 'md', 'lg']")

    nlp = spacy.load(f'ru_core_news_{model}')

    similarity_list: List[Tuple[str, str, float]] = list()
    for item1 in tqdm(sorted(list1), ncols=100, desc='progress'):
        doc1 = nlp(cleanup(item1))
        for item2 in sorted(list2):
            doc2 = nlp(cleanup(item2))
            similarity = doc1.similarity(doc2)

            # ic(cleanup(item1), cleanup(item2), similarity)

            if similarity >= threshold:
                similarity_list.append((item1.replace('\xa0', ' '), item2.replace('\xa0', ' '), similarity))

    return similarity_list


def cleanup(string: str) -> str:
    string = re.sub(r"[\s\,\.\:\;]+", " ", string)
    # string = re.sub(r"[иИ]", "ы", string)
    string = re.sub(r"[ІіїЇ]", "и", string)
    string = re.sub(r"[Єє]", "е", string)
    regex = re.compile(r"[^A-Za-zА-Яа-я0-9ІіЄєїЇ\s]+", flags=re.I)
    string = regex.sub('', string.lower().strip())
    return string
#
#
# if __name__ == "__main__":
#     string = 'Супозиторії.'
#     print(cleanup(string=string))
