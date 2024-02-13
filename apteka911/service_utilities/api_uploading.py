from typing import Tuple, List

import pandas as pd

from drug_api.api_classes import Diagnosis, Drugs, UsageColumnNames, UsageDosage, Regulations
from apteka911.page_parsing import PARSED_DATA_PATH


def upload_drugs(ip_url: str, df: pd.DataFrame) -> List[Drugs]:
    ...


def upload_regulations(api_url: str, drug_lit: List[Drugs]) -> List[Regulations]:
    ...


def df_to_drug_list(df: pd.DataFrame) -> List[Drugs]:
    ...