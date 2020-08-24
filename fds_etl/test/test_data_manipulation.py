import unittest

import pandas as pd
from numpy import nan
from pandas.testing import assert_frame_equal

import fds_etl.src.data_manipulation as dm


class TestRecodeMilitaryResponses(unittest.TestCase):

    def setUp(self):
        self.military_df = pd.DataFrame({
            'military_branch': ['U.S. Army'],
            'military_rank': ['Officer'],
            'military_specialization': ['Health Services Administration'],
            'employer_industry': [None],
            'employment_category': [None],
            'employment_type': [None],
            'is_internship': [None],
            'employer_name': [None],
            'job_title': [None],
        })

    def test_returns_the_given_df_unchanged_when_there_are_no_military_responses(self):
        df = pd.DataFrame({
            'military_branch': [None, nan, ''],
            'military_rank': [None, None, None],
            'military_specialization': [None, None, None],
            'employer_industry': [None, None, None],
            'employment_category': [None, None, None],
            'employment_type': [None, None, None],
            'is_internship': [None, None, None],
            'employer_name': [None, None, None],
            'job_title': [None, None, None]
        })
        expected = pd.DataFrame({
            'employer_industry': [None, None, None],
            'employment_category': [None, None, None],
            'employment_type': [None, None, None],
            'is_internship': [None, None, None],
            'employer_name': [None, None, None],
            'job_title': [None, None, None]
        })
        assert_frame_equal(dm.recode_military_responses(df), expected)

    def test_sets_employer_industry_to_defense(self):
        self.assertEqual(dm.recode_military_responses(self.military_df)['employer_industry'][0], 'Defense')

    def test_sets_employment_category_to_organization(self):
        self.assertEqual(dm.recode_military_responses(self.military_df)['employment_category'][0], 'Organization')

    def test_sets_employment_type_to_full_time(self):
        self.assertEqual(dm.recode_military_responses(self.military_df)['employment_type'][0], 'Full-Time')

    def test_sets_is_internship_to_false(self):
        self.assertEqual(dm.recode_military_responses(self.military_df)['is_internship'][0], False)

    def test_sets_employer_name_to_military_branch(self):
        self.assertEqual(dm.recode_military_responses(self.military_df)['employer_name'][0], 'U.S. Army')

    def test_sets_job_title_to_the_specialization_plus_the_rank(self):
        self.assertEqual(dm.recode_military_responses(self.military_df)['job_title'][0], 'Health Services Administration Officer')

    def test_drops_all_military_columns(self):
        recoded_df = dm.recode_military_responses(self.military_df)
        self.assertFalse('military_branch' in recoded_df.columns)
        self.assertFalse('military_rank' in recoded_df.columns)
        self.assertFalse('military_specialization' in recoded_df.columns)


class TestIsJHU(unittest.TestCase):

    def test_none_is_not_jhu(self):
        self.assertFalse(dm.is_jhu(None))

    def test_nan_is_not_jhu(self):
        self.assertFalse(dm.is_jhu(nan))

    def test_empty_str_is_not_jhu(self):
        self.assertFalse(dm.is_jhu(''))

    def test_simple_hopkins_str_is_jhu(self):
        self.assertTrue(dm.is_jhu('Johns Hopkins'))

    def test_compound_hopkins_str_is_jhu(self):
        self.assertTrue(dm.is_jhu('The johns hopkins Hospital'))

    def test_complex_hopkins_str_is_jhu(self):
        self.assertTrue(dm.is_jhu('   !!!! The johnS   hOPKINS AP   L     '))


class TestAddIsJHUColumn(unittest.TestCase):

    def test_rows_with_jhu_employer_are_jhu(self):
        df = pd.DataFrame({
            'employer_name': ['Johns Hopkins APL'],
            'cont_ed_school': [None]
        })
        self.assertTrue(dm.add_is_jhu_column(df)['is_jhu'][0])

    def test_rows_with_jhu_grad_school_are_jhu(self):
        df = pd.DataFrame({
            'employer_name': [None],
            'cont_ed_school': ['Johns Hopkins Whiting School']
        })
        self.assertTrue(dm.add_is_jhu_column(df)['is_jhu'][0])

    def test_rows_without_jhu_grad_school_or_employer_are_not_jhu(self):
        df = pd.DataFrame({
            'employer_name': ['Accenture'],
            'cont_ed_school': ['Florida State']
        })
        self.assertFalse(dm.add_is_jhu_column(df)['is_jhu'][0])


class TestRecodeResponseStatusAsIsSubmitted(unittest.TestCase):

    def test_responses_with_status_submitted_are_submitted(self):
        df = pd.DataFrame({'response_status': ['submitted']})
        self.assertTrue(dm.recode_response_status_as_is_submitted(df)['is_submitted'][0])

    def test_responses_with_status_in_progress_are_not_submitted(self):
        df = pd.DataFrame({'response_status': ['in_progress']})
        self.assertFalse(dm.recode_response_status_as_is_submitted(df)['is_submitted'][0])

    def test_responses_with_no_status_are_not_submitted(self):
        df = pd.DataFrame({'response_status': [nan, None, '']})
        self.assertFalse(dm.recode_response_status_as_is_submitted(df)['is_submitted'][0])
        self.assertFalse(dm.recode_response_status_as_is_submitted(df)['is_submitted'][1])
        self.assertFalse(dm.recode_response_status_as_is_submitted(df)['is_submitted'][2])

    def test_drops_response_status_column(self):
        df = pd.DataFrame({'response_status': ['submitted']})
        self.assertFalse('response_status' in dm.recode_response_status_as_is_submitted(df).columns)


class TestConsolidateLDLNPS(unittest.TestCase):

    def test_creates_max_nps_column_taking_the_highest_of_three_nps_scores(self):
        df = pd.DataFrame({'ldl_nps_1': [7], 'ldl_nps_2': [8], 'ldl_nps_3': [9]})
        self.assertEqual(dm.consolidate_ldl_nps(df)['max_ldl_nps'][0], 9)

    def test_creates_min_nps_column_taking_the_lowest_of_three_nps_scores(self):
        df = pd.DataFrame({'ldl_nps_1': [7], 'ldl_nps_2': [8], 'ldl_nps_3': [9]})
        self.assertEqual(dm.consolidate_ldl_nps(df)['min_ldl_nps'][0], 7)

    def test_drops_original_nps_columns(self):
        df = pd.DataFrame({'ldl_nps_1': [7], 'ldl_nps_2': [8], 'ldl_nps_3': [9]})
        self.assertFalse('ldl_nps_1' in dm.consolidate_ldl_nps(df).columns)
        self.assertFalse('ldl_nps_2' in dm.consolidate_ldl_nps(df).columns)
        self.assertFalse('ldl_nps_3' in dm.consolidate_ldl_nps(df).columns)


class TestSplitWorkingOutcomesIntoFullAndPartTime(unittest.TestCase):

    def test_working_outcomes_with_part_time_type_become_working_part_time(self):
        df = pd.DataFrame({'outcome': ['Working'], 'employment_type': ['Part-Time'], 'is_internship': [nan]})
        self.assertEqual(dm.split_working_outcomes_into_full_and_part_time(df)['outcome'][0], 'Working (Part-Time/Internship)')

    def test_working_outcomes_with_full_time_type_become_working_full_time(self):
        df = pd.DataFrame({'outcome': ['Working'], 'employment_type': ['Full-Time'], 'is_internship': [False]})
        self.assertEqual(dm.split_working_outcomes_into_full_and_part_time(df)['outcome'][0], 'Working (Full-Time)')

    def test_internships_become_working_part_time(self):
        df = pd.DataFrame({'outcome': ['Working'], 'employment_type': ['Full-Time'], 'is_internship': [True]})
        self.assertEqual(dm.split_working_outcomes_into_full_and_part_time(df)['outcome'][0], 'Working (Part-Time/Internship)')

    def test_drops_employment_type_and_is_internship_columns(self):
        df = pd.DataFrame({'outcome': ['Working'], 'employment_type': ['Full-Time'], 'is_internship': [True]})
        recoded_df = dm.split_working_outcomes_into_full_and_part_time(df)
        self.assertFalse('employment_type' in recoded_df.columns)
        self.assertFalse('is_internship' in recoded_df.columns)


class TestSplitStillLookingOutcomeIntoWorkAndSchool(unittest.TestCase):

    def test_still_looking_outcomes_with_employment_option_become_still_looking_employment(self):
        df = pd.DataFrame({'outcome': ['Still Looking'], 'still_seeking_option': ['Employment']})
        self.assertEqual(dm.split_still_looking_outcomes_into_work_and_school(df)['outcome'][0], 'Still Looking (Employment)')

    def test_still_looking_outcomes_with_cont_ed_option_become_still_looking_cont_ed(self):
        df = pd.DataFrame({'outcome': ['Still Looking'], 'still_seeking_option': ['Continuing Education']})
        self.assertEqual(dm.split_still_looking_outcomes_into_work_and_school(df)['outcome'][0], 'Still Looking (Continuing Education)')

    def test_drops_still_seeking_option_column(self):
        df = pd.DataFrame({'outcome': ['Still Looking'], 'still_seeking_option': ['Continuing Education']})
        recoded_df = dm.split_still_looking_outcomes_into_work_and_school(df)
        self.assertFalse('still_seeking_option' in recoded_df.columns)


class TestRecodeFellowshipResponses(unittest.TestCase):

    def test_fellowship_responses_have_outcome_of_fellowship(self):
        df = pd.DataFrame({'outcome': ['Working'], 'is_fellowship': ['Yes'], 'employer_name': ['NIH']})
        self.assertEqual(dm.recode_fellowship_responses(df)['outcome'][0], 'Fellowship')

    def test_recodes_employer_name_as_fellowship_org(self):
        df = pd.DataFrame({'outcome': ['Working'], 'is_fellowship': ['Yes'], 'employer_name': ['NIH']})
        self.assertEqual(dm.recode_fellowship_responses(df)['fellowship_org'][0], 'NIH')

    def test_drops_is_fellowship_column(self):
        df = pd.DataFrame({'outcome': ['Working'], 'is_fellowship': ['Yes'], 'employer_name': ['NIH']})
        self.assertFalse('is_fellowship' in dm.recode_fellowship_responses(df).columns)


class TestRecodeBooleanColumnsToExcelFriendlyStrings(unittest.TestCase):

    def test_converts_blanks_and_nans_to_empty_string(self):
        df = pd.DataFrame({'field': [nan, None, '']})
        expected = pd.DataFrame({'field': ['', '', '']})
        assert_frame_equal(expected, dm.recode_boolean_columns_to_excel_friendly_strings(df, ['field']))

    def test_converts_0_to_false_string(self):
        df = pd.DataFrame({'field': [0]})
        self.assertEqual(dm.recode_boolean_columns_to_excel_friendly_strings(df, ['field'])['field'][0], 'FALSE')

    def test_converts_1_to_true_string(self):
        df = pd.DataFrame({'field': [1]})
        self.assertEqual(dm.recode_boolean_columns_to_excel_friendly_strings(df, ['field'])['field'][0], 'TRUE')
