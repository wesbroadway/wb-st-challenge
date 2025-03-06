from unittest import TestCase

from wb_st_challenge import processor

from . import fixtures


class TestProcessor(TestCase):
    def test_process_data(self):
        fixtures_and_expectation = [
            (fixtures.get_set_1(), fixtures.get_set_1_expectation()),
            # (fixtures.get_set_2(), fixtures.get_set_2_expectation()),
            # (fixtures.get_set_3(), fixtures.get_set_3_expectation()),
            # (fixtures.get_set_4(), fixtures.get_set_4_expectation()),
            # (fixtures.get_set_5(), fixtures.get_set_5_expectation()),
        ]

        for index, (fixture, expectation) in enumerate(fixtures_and_expectation):
            with self.subTest(set=index + 1):
                result = processor.process_data(fixture)
                self.assertIsNotNone(result, msg="Business logic has not been developed yet")
