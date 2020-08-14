import pandas as pd

from fds_etl.src.config import CONFIG
from fds_etl.src.file_parsers import csv_to_dict


def execute():
    df = read_raw_response_data()
    column_name_map = csv_to_dict(CONFIG['column_name_mapping_file'])
    df = df.rename(columns=column_name_map)
    print(df.info())


def read_raw_response_data() -> pd.DataFrame:
    ugrad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['undergraduate']], ignore_index=True)
    ugrad_df['education_level'] = 'Undergraduate'
    grad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['masters']], ignore_index=True)
    grad_df['education_level'] = 'Masters'
    return pd.concat([ugrad_df, grad_df])
