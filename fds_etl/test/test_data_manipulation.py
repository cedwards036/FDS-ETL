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
