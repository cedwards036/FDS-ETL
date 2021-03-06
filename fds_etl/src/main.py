import pandas as pd

import fds_etl.src.data_manipulation as dm
from fds_etl.src.config import CONFIG
from fds_etl.src.file_parsers import csv_to_dict, single_column_to_list


def execute():
    df = read_raw_response_data()
    df = drop_unnecessary_columns(df)
    df = rename_columns(df)
    df = add_student_demographic_data(df)
    df = add_fds_year(df)
    df = split_locations_into_city_state_country(df)
    df = add_cont_ed_major_supplemental_info(df)
    df = dm.recode_response_status_as_is_submitted(df)
    df = dm.recode_military_responses(df)
    df = dm.recode_fellowship_responses(df)
    df = dm.split_working_outcomes_into_full_and_part_time(df)
    df = dm.split_still_looking_outcomes_into_work_and_school(df)
    df = dm.add_consolidated_ldl_nps_columns(df)
    df = dm.add_is_jhu_column(df)
    df = expand_activities_at_jhu_into_multiple_columns(df)
    df = recode_boolean_columns_to_excel_friendly_strings(df)
    df = drop_columns_needed_for_cleaning_but_not_for_analysis(df)
    shortform_df = dm.create_shortform_df(df, ['jhu_major', 'jhu_degree', 'jhu_college'])
    print(df.info())
    print(shortform_df.info())
    for filepath in CONFIG['longform_output_files']:
        df.to_excel(filepath, index=False)
    for filepath in CONFIG['shortform_output_files']:
        shortform_df.to_excel(filepath, index=False)


def read_raw_response_data() -> pd.DataFrame:
    ugrad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['undergraduate']], ignore_index=True)
    ugrad_df['education_level'] = 'Undergraduate'
    grad_df = pd.concat([pd.read_csv(f) for f in CONFIG['source_files']['masters']], ignore_index=True)
    grad_df['education_level'] = 'Masters'
    return pd.concat([ugrad_df, grad_df], sort=True)


def drop_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = single_column_to_list(CONFIG['dropped_columns_file'], skip_header=False)
    return df.drop(columns=columns_to_drop)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    column_name_map = csv_to_dict(CONFIG['column_name_mapping_file'])
    return df.rename(columns=column_name_map)


def add_student_demographic_data(df: pd.DataFrame) -> pd.DataFrame:
    demographics = pd.read_excel(CONFIG["student_demographics_file"])
    demographics['hopkins_id'] = demographics['hopkins_id'].str.lower()
    return df.merge(demographics, how='left', on='hopkins_id')


def split_locations_into_city_state_country(df: pd.DataFrame) -> pd.DataFrame:
    locations = pd.read_excel(CONFIG["location_mapping_file"])
    return df.merge(locations, how='left', left_on='location', right_on='raw_location').drop(columns=['location', 'raw_location'])


def add_cont_ed_major_supplemental_info(df: pd.DataFrame) -> pd.DataFrame:
    df['cont_ed_major_group'] = ''
    df['cont_ed_degree'] = ''
    return df


def add_fds_year(df: pd.DataFrame) -> pd.DataFrame:
    df['fds_year'] = CONFIG['fds_year']
    return df


def drop_columns_needed_for_cleaning_but_not_for_analysis(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=['pay_schedule'])


def recode_boolean_columns_to_excel_friendly_strings(df: pd.DataFrame) -> pd.DataFrame:
    columns = ['is_athlete', 'is_first_gen', 'is_pell_eligible', 'is_urm']
    return dm.recode_boolean_columns_to_excel_friendly_strings(df, columns)


def expand_activities_at_jhu_into_multiple_columns(df: pd.DataFrame) -> pd.DataFrame:
    value_to_col_name_map = {
        'Independent research with a faculty member': 'did_faculty_research',
        'Other research': 'did_other_research',
        'Internship/practicum': 'did_internship',
        'Study abroad': 'did_study_abroad',
        'On campus job': 'had_on_campus_job',
        'Leadership in student organization': 'did_student_org_leadership',
        'Entrepreneurship': 'did_entrepreneurship',
        'Experiential learning trip': 'did_exp_learning_trip',
        'Community impact and service': 'did_community_service',
        'Connection with a mentor': 'connected_with_mentor',
    }
    return dm.expand_experiential_learning_column(df, value_to_col_name_map)
