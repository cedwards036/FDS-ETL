import re

import pandas as pd


def recode_military_responses(df: pd.DataFrame) -> pd.DataFrame:
    military_responses = ~df['military_branch'].isna() & ~(df['military_branch'] == '')
    df.loc[military_responses, ['employer_industry', 'employment_category', 'employment_type', 'is_internship']] = [
        'Defense',  # industry
        'Organization',  # category
        'Full-Time',  # type,
        False,  # is_internship
    ]
    df.loc[military_responses, 'employer_name'] = df.loc[military_responses, 'military_branch']
    job_title = df.loc[military_responses, 'military_specialization'] + ' ' + df.loc[military_responses, 'military_rank']
    df.loc[military_responses, 'job_title'] = job_title
    df = df.drop(columns=['military_branch', 'military_rank', 'military_specialization'])
    return df


def is_jhu(org_name: str) -> bool:
    if not isinstance(org_name, str):
        return False
    else:
        return org_name and re.match(r'.*johns\s+hopkins.*', org_name.lower()) is not None


def add_is_jhu_column(df: pd.DataFrame) -> pd.DataFrame:
    df['is_jhu'] = df.apply(lambda row: is_jhu(row['employer_name']) or is_jhu(row['cont_ed_school']), axis=1)
    return df


def recode_response_status_as_is_submitted(df: pd.DataFrame) -> pd.DataFrame:
    df['is_submitted'] = df['response_status'] == 'submitted'
    return df.drop(columns=['response_status'])
