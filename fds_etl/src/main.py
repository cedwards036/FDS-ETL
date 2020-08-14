import pandas as pd

from fds_etl.src.config import CONFIG


def execute():
    ugrad_df = pd.read_csv(CONFIG['source_files']['undergraduate'][0])
    grad_df = pd.read_csv(CONFIG['source_files']['masters'][0])
    print(ugrad_df.info())
    print(grad_df.info())
