import pandas as pd

from fds_etl.src.config import CONFIG
from fds_etl.src.file_parsers import csv_to_dict, single_column_to_list


def execute():
    df = read_raw_response_data()
    df = drop_unnecessary_columns(df)
    df = rename_columns(df)
    df = add_student_demographic_data(df)
    print(df.info())


def read_raw_response_data() -> pd.DataFrame:
    ugrad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['undergraduate']], ignore_index=True)
    ugrad_df['education_level'] = 'Undergraduate'
    grad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['masters']], ignore_index=True)
    grad_df['education_level'] = 'Masters'
    return pd.concat([ugrad_df, grad_df], sort=True)


def drop_unnecessary_columns(df) -> pd.DataFrame:
    columns_to_drop = single_column_to_list(CONFIG['dropped_columns_file'], skip_header=False)
    return df.drop(columns=columns_to_drop)


def rename_columns(df) -> pd.DataFrame:
    column_name_map = csv_to_dict(CONFIG['column_name_mapping_file'])
    return df.rename(columns=column_name_map)


def add_student_demographic_data(df: pd.DataFrame) -> pd.DataFrame:
    demographics = pd.read_excel(CONFIG["student_demographics_file"])
    return df.merge(demographics, how='left', on='hopkins_id')
