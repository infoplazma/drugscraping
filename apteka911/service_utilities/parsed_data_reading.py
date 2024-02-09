from pprint import pprint
import pandas as pd

from apteka911.page_parsing import PARSED_DATA_PATH


df = pd.read_csv(PARSED_DATA_PATH)

pprint(sorted(df.columns.tolist()))
