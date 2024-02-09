from pprint import pprint
import pandas as pd

import settings

from apteka911.page_parsing import PARSED_DATA_PATH


df = pd.read_csv(PARSED_DATA_PATH)

pprint(sorted(df.columns.tolist()))
print(f"{settings.API_URL=}")
