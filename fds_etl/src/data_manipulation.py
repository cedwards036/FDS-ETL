import re
from typing import List

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


def calculate_min_and_max_ldl_nps(df: pd.DataFrame) -> pd.DataFrame:
    nps_columns = ['ldl_nps_1', 'ldl_nps_2', 'ldl_nps_3']
    df['max_ldl_nps'] = df[nps_columns].max(axis=1)
    df['min_ldl_nps'] = df[nps_columns].min(axis=1)
    return df.drop(columns=nps_columns)


def split_working_outcomes_into_full_and_part_time(df: pd.DataFrame) -> pd.DataFrame:
    part_time_rows = (df['outcome'] == 'Working') & (df['employment_type'] == 'Part-Time')
    full_time_rows = (df['outcome'] == 'Working') & (df['employment_type'] == 'Full-Time')
    internships = (df['outcome'] == 'Working') & (df['is_internship'] == True)
    df.loc[part_time_rows, 'outcome'] = 'Working (Part-Time/Internship)'
    df.loc[full_time_rows, 'outcome'] = 'Working (Full-Time)'
    df.loc[internships, 'outcome'] = 'Working (Part-Time/Internship)'
    return df.drop(columns=['is_internship', 'employment_type'])


def split_still_looking_outcomes_into_work_and_school(df: pd.DataFrame) -> pd.DataFrame:
    still_looking_employment_rows = (df['outcome'] == 'Still Looking') & (df['still_seeking_option'] == 'Employment')
    still_looking_cont_ed_rows = (df['outcome'] == 'Still Looking') & (df['still_seeking_option'] == 'Continuing Education')
    df.loc[still_looking_employment_rows, 'outcome'] = 'Still Looking (Employment)'
    df.loc[still_looking_cont_ed_rows, 'outcome'] = 'Still Looking (Continuing Education)'
    return df.drop(columns=['still_seeking_option'])


def recode_fellowship_responses(df: pd.DataFrame) -> pd.DataFrame:
    is_fellowship = df['is_fellowship'] == 'Yes'
    df.loc[is_fellowship, 'outcome'] = 'Fellowship'
    df.loc[is_fellowship, 'fellowship_org'] = df.loc[is_fellowship, 'employer_name']
    return df.drop(columns=['is_fellowship'])


def recode_boolean_columns_to_excel_friendly_strings(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    df[columns] = df[columns].fillna('').replace({0: 'FALSE', 1: 'TRUE'})
    return df
