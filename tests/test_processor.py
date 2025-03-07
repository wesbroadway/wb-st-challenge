from datetime import date
from pathlib import Path
from random import shuffle
from unittest import TestCase
from unittest.mock import patch

from wb_st_challenge import processor
from wb_st_challenge.constants import (
    HIGH_COST_FULL_DAY_RATE,
    HIGH_COST_TRAVEL_DAY_RATE,
    LOW_COST_FULL_DAY_RATE,
    LOW_COST_TRAVEL_DAY_RATE,
)

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

    def test_parse_data_into_list_of_projects(self):
        with self.subTest('default behavior'):
            # The key feature of this data is that the sorting prioritizes the end date and THEN the start date values
            data = [
                {'start_date': '2024-02-10', 'end_date': '2024-02-11', 'cost_zone': 'SHOULD BE FIRST'},
                {'start_date': '2024-02-12', 'end_date': '2024-02-15', 'cost_zone': 'SHOULD BE THIRD'},
                {'start_date': '2024-02-13', 'end_date': '2024-02-13', 'cost_zone': 'SHOULD BE SECOND'},
            ]

            result = processor.parse_data_into_list_of_projects(data)

            # Indexes 0 and 1 match up to the mock side_effects from above, but have now been sorted
            # Also, our cost zones should be lower-cased
            self.assertEqual(result[0][0], date(2024, 2, 10))
            self.assertEqual(result[0][1], date(2024, 2, 11))
            self.assertEqual(result[0][2], 'should be first')

            self.assertEqual(result[1][0], date(2024, 2, 13))
            self.assertEqual(result[1][1], date(2024, 2, 13))
            self.assertEqual(result[1][2], 'should be second')

            self.assertEqual(result[2][0], date(2024, 2, 12))
            self.assertEqual(result[2][1], date(2024, 2, 15))
            self.assertEqual(result[2][2], 'should be third')

        with self.subTest('empty list'):
            self.assertEqual(processor.parse_data_into_list_of_projects([]), [])

        with self.subTest('with the list in virtually any order (using shuffle 10 times)'):
            for _ in range(0, 10):
                shuffle(data)
                result = processor.parse_data_into_list_of_projects(data)
                self.assertEqual(result[0][0], date(2024, 2, 10))
                self.assertEqual(result[1][0], date(2024, 2, 13))
                self.assertEqual(result[2][0], date(2024, 2, 12))


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
            (fixtures.get_set_6(), fixtures.get_set_6_expectation()),
        ]

        for index, (fixture, expectation) in enumerate(fixtures_and_expectation):
            with self.subTest(set=index + 1):
                result = processor.process_data(fixture)
                self.assertEqual(result.total, expectation.total)
                self.assertEqual(result.high_cost_full_days, expectation.high_cost_full_days)
                self.assertEqual(result.high_cost_travel_days, expectation.high_cost_travel_days)
                self.assertEqual(result.low_cost_full_days, expectation.low_cost_full_days)
                self.assertEqual(result.low_cost_travel_days, expectation.low_cost_travel_days)

    def test_process_data_with_empty_list(self):
        result = processor.process_data([])
        self.assertIsInstance(result, processor.ReimbursementResult)
        self.assertEqual(result.total, 0)
        self.assertEqual(result.high_cost_full_days, 0)
        self.assertEqual(result.high_cost_travel_days, 0)
        self.assertEqual(result.low_cost_full_days, 0)
        self.assertEqual(result.low_cost_travel_days, 0)


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


@patch("wb_st_challenge.processor.make_is_travel_day_tester", return_value=lambda d: False)
class CalculateDailyRatesTest(TestCase):
    def test_one_high_cost_day(self, mock_travel_tester):
        mock_travel_tester.return_value = lambda p: True
        merged = [(date(2024, 10, 1), date(2024, 10, 1), 'high')]
        expected = {date(2024, 10, 1): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True)}

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_two_high_cost_days(self, mock_travel_tester):
        mock_travel_tester.return_value = lambda p: True
        merged = [(date(2024, 10, 1), date(2024, 10, 2), 'high')]
        expected = {
            date(2024, 10, 1): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True),
            date(2024, 10, 2): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_multi_high_cost_days(self, mock_travel_tester):
        mock_travel_tester.return_value = lambda d: d in [date(2024, 10, 1), date(2024, 10, 5)]
        merged = [(date(2024, 10, 1), date(2024, 10, 5), 'high')]
        expected = {
            date(2024, 10, 1): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True),
            date(2024, 10, 2): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 3): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 4): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 5): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_one_low_cost_day(self, mock_travel_tester):
        mock_travel_tester.return_value = lambda p: True
        merged = [(date(2024, 10, 1), date(2024, 10, 1), 'low')]
        expected = {date(2024, 10, 1): (LOW_COST_TRAVEL_DAY_RATE, 'low', True)}

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_two_low_cost_days(self, mock_travel_tester):
        mock_travel_tester.return_value = lambda p: True
        merged = [(date(2024, 10, 1), date(2024, 10, 2), 'low')]
        expected = {
            date(2024, 10, 1): (LOW_COST_TRAVEL_DAY_RATE, 'low', True),
            date(2024, 10, 2): (LOW_COST_TRAVEL_DAY_RATE, 'low', True),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_multi_low_cost_days(self, mock_travel_tester):
        mock_travel_tester.return_value = lambda d: d in [date(2024, 10, 1), date(2024, 10, 5)]
        merged = [(date(2024, 10, 1), date(2024, 10, 5), 'low')]
        expected = {
            date(2024, 10, 1): (LOW_COST_TRAVEL_DAY_RATE, 'low', True),
            date(2024, 10, 2): (LOW_COST_FULL_DAY_RATE, 'low', False),
            date(2024, 10, 3): (LOW_COST_FULL_DAY_RATE, 'low', False),
            date(2024, 10, 4): (LOW_COST_FULL_DAY_RATE, 'low', False),
            date(2024, 10, 5): (LOW_COST_TRAVEL_DAY_RATE, 'low', True),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_high_cost_full_day_overrides_low_cost(self, *_):
        """Test that a high-cost project overrides a low-cost one on the same day."""
        merged = [
            (date(2024, 10, 1), date(2024, 10, 3), 'low'),
            (date(2024, 10, 2), date(2024, 10, 2), 'high'),
        ]
        expected = {
            date(2024, 10, 1): (LOW_COST_FULL_DAY_RATE, 'low', False),
            date(2024, 10, 2): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 3): (LOW_COST_FULL_DAY_RATE, 'low', False),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_high_cost_travel_day_overrides_low_cost(self, mock_travel_tester):
        """Test that a high-cost project overrides a low-cost one on the same day."""
        mock_travel_tester.return_value = lambda d: d in [date(2024, 10, 1), date(2024, 10, 3)]
        merged = [
            (date(2024, 10, 1), date(2024, 10, 1), 'high'),
            (date(2024, 10, 1), date(2024, 10, 3), 'low'),
            (date(2024, 10, 3), date(2024, 10, 3), 'high'),
        ]
        expected = {
            date(2024, 10, 1): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True),
            date(2024, 10, 2): (LOW_COST_FULL_DAY_RATE, 'low', False),
            date(2024, 10, 3): (HIGH_COST_TRAVEL_DAY_RATE, 'high', True),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

        with self.subTest('shuffled 10x'):
            for _ in range(0, 10):
                shuffle(merged)
                self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_non_overlapping_projects(self, *_):
        """NOTE: This test violates the rules of travel days at the start/end of a sequence."""
        merged = [
            (date(2024, 10, 1), date(2024, 10, 2), 'high'),
            (date(2024, 10, 4), date(2024, 10, 5), 'low'),
        ]
        expected = {
            date(2024, 10, 1): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 2): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 4): (LOW_COST_FULL_DAY_RATE, 'low', False),
            date(2024, 10, 5): (LOW_COST_FULL_DAY_RATE, 'low', False),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_high_cost_low_cost_full_day_overlap(self, *_):
        """NOTE: This test violates the rules of travel days at the start/end of a sequence."""
        merged = [
            (date(2024, 10, 1), date(2024, 10, 1), 'low'),
            (date(2024, 10, 1), date(2024, 10, 1), 'high'),
        ]
        expected = {
            date(2024, 10, 1): (HIGH_COST_FULL_DAY_RATE, 'high', False),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

        with self.subTest('reversed order'):
            merged = [
                (date(2024, 10, 1), date(2024, 10, 1), 'high'),
                (date(2024, 10, 1), date(2024, 10, 1), 'low'),
            ]
            expected = {
                date(2024, 10, 1): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            }

            self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_high_cost_full_day_overlap(self, *_):
        """NOTE: This test violates the rules of travel days at the start/end of a sequence."""
        merged = [
            (date(2024, 10, 1), date(2024, 10, 3), 'high'),
            (date(2024, 10, 2), date(2024, 10, 2), 'high'),
        ]
        expected = {
            date(2024, 10, 1): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 2): (HIGH_COST_FULL_DAY_RATE, 'high', False),
            date(2024, 10, 3): (HIGH_COST_FULL_DAY_RATE, 'high', False),
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)

    def test_empty_input_returns_empty_dict(self, *_):
        self.assertEqual(processor.calculate_daily_rates([]), {})

    def test_duplicate_low_cost_travel_day_does_not_override(self, mock_travel_tester):
        """Test that a duplicate low-cost travel day does not override itself."""
        mock_travel_tester.return_value = lambda p: True
        merged = [
            (date(2024, 10, 1), date(2024, 10, 1), 'low'),  # First travel day
            (date(2024, 10, 1), date(2024, 10, 1), 'low'),  # Duplicate travel day
        ]
        expected = {
            date(2024, 10, 1): (LOW_COST_TRAVEL_DAY_RATE, 'low', True),  # Stays the same
        }

        self.assertEqual(processor.calculate_daily_rates(merged), expected)
