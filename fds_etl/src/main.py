import pandas as pd

from fds_etl.src.config import CONFIG


def execute():
    ugrad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['undergraduate']], ignore_index=True)
    grad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['masters']], ignore_index=True)
    print(ugrad_df.info())
    print(grad_df.info())
