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
