import pandas as pd

from fds_etl.src.config import CONFIG


def execute():
    ugrad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['undergraduate']], ignore_index=True)
    ugrad_df['education_level'] = 'Undergraduate'
    grad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['masters']], ignore_index=True)
    grad_df['education_level'] = 'Masters'
    df = pd.concat([ugrad_df, grad_df])
    print(df.info())
