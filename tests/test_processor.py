from datetime import date
from pathlib import Path
from unittest import TestCase
from unittest.mock import call, patch

from wb_st_challenge import processor

from . import fixtures


class ProcesserGeneralTest(TestCase):
    def test_parse_date(self):
        fixtures_and_expectations = [
            ('2024-01-02', date(2024, 1, 2)),
            ('2024-02-01', date(2024, 2, 1)),
        ]

        for _date, expected in fixtures_and_expectations:
            with self.subTest(date=_date, expected=expected):
                self.assertEqual(processor.parse_date(_date), expected)

        with self.subTest('Invalid values raise a TypeError or ValueError'):
            with self.assertRaises(ValueError):
                processor.parse_date('January 5th, 2023')
            with self.assertRaises(TypeError):
                processor.parse_date([1, 2, 3, 4, 5])
            with self.assertRaises(TypeError):
                processor.parse_date(date(2024, 1, 2))

    @patch('wb_st_challenge.processor.parse_date')
    def test_parse_data_into_list_of_projects(self, m_parse_date):
        with self.subTest('default behavior'):
            # m_parse_date is called twice per row and we have three rows. By returning these values
            # we can verify that our end result is what we expect it to be
            m_parse_date.side_effect = [*(1, 1), *(2, 1), *(1, 3)]

            # The key feature of this data is that the start_date values are in alpha order, while the cost zones are
            # labelled with the expected position AFTER sorting according to the values returned by the patch.
            data = [
                {'start_date': 'AAA', 'end_date': 'BBB', 'cost_zone': 'SHOULD BE FIRST'},
                {'start_date': 'CCC', 'end_date': 'DDD', 'cost_zone': 'SHOULD BE THIRD'},
                {'start_date': 'EEE', 'end_date': 'FFF', 'cost_zone': 'SHOULD BE SECOND'},
            ]

            result = processor.parse_data_into_list_of_projects(data)

            m_parse_date.assert_has_calls(
                [call('AAA'), call('BBB'), call('CCC'), call('DDD'), call('EEE'), call('FFF')]
            )

            # Indexes 0 and 1 match up to the mock side_effects from above, but have now been sorted!
            # Also, our cost zones should be lower-cased
            self.assertEqual(result[0][0], 1)
            self.assertEqual(result[0][1], 1)
            self.assertEqual(result[0][2], 'should be first')

            self.assertEqual(result[1][0], 1)
            self.assertEqual(result[1][1], 3)
            self.assertEqual(result[1][2], 'should be second')

            self.assertEqual(result[2][0], 2)
            self.assertEqual(result[2][1], 1)
            self.assertEqual(result[2][2], 'should be third')

        with self.subTest('empty list'):
            self.assertEqual(processor.parse_data_into_list_of_projects([]), [])


class MergeProjectsTest(TestCase):
    def test_merge_same_cost_zone(self):
        projects = [
            (date(2024, 10, 1), date(2024, 10, 3), "low"),
            (date(2024, 10, 4), date(2024, 10, 6), "low"),  # Adjacent, should merge
        ]
        expected = [
            (date(2024, 10, 1), date(2024, 10, 6), "low"),  # Merged
        ]
        self.assertEqual(processor.merge_projects(projects), expected)

    def test_different_cost_zones(self):
        projects = [
            (date(2024, 10, 1), date(2024, 10, 3), "low"),
            (date(2024, 10, 4), date(2024, 10, 6), "high"),  # Different cost zone, should not merge
        ]
        expected = [
            (date(2024, 10, 1), date(2024, 10, 3), "low"),
            (date(2024, 10, 4), date(2024, 10, 6), "high"),
        ]
        self.assertEqual(processor.merge_projects(projects), expected)

    def test_overlapping_projects(self):
        projects = [
            (date(2024, 10, 1), date(2024, 10, 5), "high"),
            (date(2024, 10, 4), date(2024, 10, 8), "high"),  # Overlaps, should merge
        ]
        expected = [
            (date(2024, 10, 1), date(2024, 10, 8), "high"),  # Merged
        ]
        self.assertEqual(processor.merge_projects(projects), expected)

    def test_gap_between_projects(self):
        projects = [
            (date(2024, 10, 1), date(2024, 10, 3), "low"),
            (date(2024, 10, 5), date(2024, 10, 7), "low"),  # Gap (10/4), should not merge
        ]
        expected = [
            (date(2024, 10, 1), date(2024, 10, 3), "low"),
            (date(2024, 10, 5), date(2024, 10, 7), "low"),
        ]
        self.assertEqual(processor.merge_projects(projects), expected)

    def test_multiple_merges(self):
        projects = [
            (date(2024, 10, 1), date(2024, 10, 2), "low"),
            (date(2024, 10, 3), date(2024, 10, 4), "low"),
            (date(2024, 10, 5), date(2024, 10, 6), "low"),
        ]
        expected = [
            (date(2024, 10, 1), date(2024, 10, 6), "low"),  # All merged
        ]
        self.assertEqual(processor.merge_projects(projects), expected)

    def test_single_project(self):
        projects = [(date(2024, 10, 1), date(2024, 10, 3), "high")]
        expected = [(date(2024, 10, 1), date(2024, 10, 3), "high")]
        self.assertEqual(processor.merge_projects(projects), expected)

    def test_empty_list(self):
        self.assertEqual(processor.merge_projects([]), [])


class ProcessDataTest(TestCase):
    def test_process_data(self):
        fixtures_and_expectation = [
            (fixtures.get_set_1(), fixtures.get_set_1_expectation()),
            (fixtures.get_set_2(), fixtures.get_set_2_expectation()),
            (fixtures.get_set_3(), fixtures.get_set_3_expectation()),
            (fixtures.get_set_4(), fixtures.get_set_4_expectation()),
            (fixtures.get_set_5(), fixtures.get_set_5_expectation()),
        ]

        for index, (fixture, expectation) in enumerate(fixtures_and_expectation):
            with self.subTest(set=index + 1):
                result = processor.process_data(fixture)
                self.assertEqual(result.total, expectation.total)
                self.assertEqual(result.high_cost_full_days, expectation.high_cost_full_days)
                self.assertEqual(result.high_cost_travel_days, expectation.high_cost_travel_days)
                self.assertEqual(result.low_cost_full_days, expectation.low_cost_full_days)
                self.assertEqual(result.low_cost_travel_days, expectation.low_cost_travel_days)


class GetDataFromCSVTest(TestCase):
    def test_normal_behavior_using_our_example_file(self):
        filename = Path(__file__).parent.parent / 'data_file_example.csv'
        result = processor.get_data_from_csv(filename)
        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0]['start_date'],
            '2024-01-25',
            msg='Warning: brittle test! Might break if the example data file has been altered.',
        )

    def test_with_invalid_filename(self):
        filename = 'doesnt_exists.xzy123'
        with self.assertRaises(FileNotFoundError):
            processor.get_data_from_csv(filename)
