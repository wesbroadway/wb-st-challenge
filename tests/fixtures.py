"""
This module contains fixtures and expectations for our tests. They are wrapped in
getter functions in order to prevent any mutation across tests.

Usage:

```
from tests import fixtures

test_fixtures_and_their_expectations = [
    (get_set_1(), get_set_1_expectation()),
    (get_set_2(), get_set_2_expectation()),
    ... etc ...
]
```

"""
import copy

from dataclasses import dataclass

from wb_st_challenge.constants import (
    HIGH_COST_FULL_DAY_RATE,
    HIGH_COST_TRAVEL_DAY_RATE,
    LOW_COST_FULL_DAY_RATE,
    LOW_COST_TRAVEL_DAY_RATE,
)


@dataclass
class Expectation:
    total: int = 0
    high_cost_full_days: int = 0
    high_cost_travel_days: int = 0
    low_cost_full_days: int = 0
    low_cost_travel_days: int = 0


# ------------------------------------
# Set 1
# ------------------------------------


def get_set_1() -> list:
    return copy.deepcopy(
        [
            {'start_date': '2024-10-01', 'end_date': '2024-10-04', 'cost_zone': 'low'},
        ]
    )


def get_set_1_expectation() -> Expectation:
    return Expectation(
        total=(LOW_COST_TRAVEL_DAY_RATE * 2) + (LOW_COST_FULL_DAY_RATE * 2),
        high_cost_full_days=0,
        high_cost_travel_days=0,
        low_cost_full_days=2,
        low_cost_travel_days=2,
    )


# ------------------------------------
# Set 2
# ------------------------------------


def get_set_2() -> list:
    return copy.deepcopy(
        [
            # 1 low cost travel day
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'low'},
            # 5 high cost full days
            {'start_date': '2024-10-02', 'end_date': '2024-10-06', 'cost_zone': 'high'},
            # first day overlaps and is superceded by the previous entry.
            # 2 low cost full days, and 1 low cost travel day
            {'start_date': '2024-10-06', 'end_date': '2024-10-09', 'cost_zone': 'low'},
        ]
    )


def get_set_2_expectation() -> Expectation:
    return Expectation(
        # NOTE: the highest daily rate is the rate to be used when there's overlap with high/low cost zones
        total=(LOW_COST_TRAVEL_DAY_RATE * 2) + (LOW_COST_FULL_DAY_RATE * 2) + (HIGH_COST_FULL_DAY_RATE * 5),
        high_cost_full_days=5,
        high_cost_travel_days=0,
        low_cost_full_days=2,
        low_cost_travel_days=2,
    )


# ------------------------------------
# Set 3
# ------------------------------------


def get_set_3() -> list:
    return copy.deepcopy(
        [
            {'start_date': '2024-09-30', 'end_date': '2024-10-03', 'cost_zone': 'low'},
            {'start_date': '2024-10-05', 'end_date': '2024-10-07', 'cost_zone': 'high'},
            {'start_date': '2024-10-08', 'end_date': '2024-10-08', 'cost_zone': 'high'},
        ]
    )


def get_set_3_expectation() -> Expectation:
    return Expectation(
        total=(
            (LOW_COST_TRAVEL_DAY_RATE * 2)
            + (LOW_COST_FULL_DAY_RATE * 2)
            + (HIGH_COST_TRAVEL_DAY_RATE * 2)
            + (HIGH_COST_FULL_DAY_RATE * 2)
        ),
        high_cost_full_days=2,
        high_cost_travel_days=2,
        low_cost_full_days=2,
        low_cost_travel_days=2,
    )


# ------------------------------------
# Set 4
# ------------------------------------


def get_set_4() -> list:
    return copy.deepcopy(
        [
            # 1 low cost travel day
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'low'},
            # ignored
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'low'},
            # 2 high cost full days
            {'start_date': '2024-10-02', 'end_date': '2024-10-03', 'cost_zone': 'high'},
            # first 2 days overlap, so ignore. 2 high cost full days, 1 high cost travel day
            {'start_date': '2024-10-02', 'end_date': '2024-10-06', 'cost_zone': 'high'},
        ]
    )


def get_set_4_expectation() -> Expectation:
    return Expectation(
        total=((LOW_COST_TRAVEL_DAY_RATE * 1) + (HIGH_COST_TRAVEL_DAY_RATE * 1) + (HIGH_COST_FULL_DAY_RATE * 4)),
        high_cost_full_days=4,
        high_cost_travel_days=1,
        low_cost_full_days=0,
        low_cost_travel_days=1,
    )


# ------------------------------------
# Set 5
# ------------------------------------


def get_set_5() -> list:
    return copy.deepcopy(
        [
            # 1 low cost travel day, ignored b/c it is overlapped by a high-cost project on same day
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'low'},
            # 1 high cost travel day
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'high'},
            # 1 low-cost full day, ignored b/c it is overlapped by a high-cost project on same day
            {'start_date': '2024-10-02', 'end_date': '2024-10-02', 'cost_zone': 'low'},
            # 1 low-cost full day, ignored b/c it is overlapped by a high-cost project on same day
            {'start_date': '2024-10-03', 'end_date': '2024-10-03', 'cost_zone': 'low'},
            # 3 high cost full days, 1 high cost travel day
            {'start_date': '2024-10-02', 'end_date': '2024-10-05', 'cost_zone': 'high'},
        ]
    )


def get_set_5_expectation() -> Expectation:
    return Expectation(
        total=(
            # NOTE: the highest daily rate is the rate to be used when there's overlap with high/low cost zones
            (LOW_COST_TRAVEL_DAY_RATE * 0)
            + (LOW_COST_FULL_DAY_RATE * 0)
            + (HIGH_COST_TRAVEL_DAY_RATE * 2)
            + (HIGH_COST_FULL_DAY_RATE * 3)
        ),
        high_cost_full_days=3,
        high_cost_travel_days=2,
        low_cost_full_days=0,
        low_cost_travel_days=0,
    )


# ------------------------------------
# Set 6
# ------------------------------------


def get_set_6() -> list:
    """
    This is almost the exact same as set 5, except we're changing the order of the first 2 projects,
    and inverting the cost zones for the other 3, which have a bit of overlapping.
    :return:
    """
    return copy.deepcopy(
        [
            # 1 high cost travel day
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'high'},
            # 1 low cost travel day, ignored b/c it is overlapped by a high-cost project on same day
            {'start_date': '2024-10-01', 'end_date': '2024-10-01', 'cost_zone': 'low'},
            # 1 high-cost full day
            {'start_date': '2024-10-02', 'end_date': '2024-10-02', 'cost_zone': 'high'},
            # 1 high-cost full day
            {'start_date': '2024-10-03', 'end_date': '2024-10-03', 'cost_zone': 'high'},
            # 1 low cost full day (2 ignored), and 1 low cost travel days
            {'start_date': '2024-10-02', 'end_date': '2024-10-05', 'cost_zone': 'low'},
        ]
    )


def get_set_6_expectation() -> Expectation:
    return Expectation(
        total=(
            # NOTE: the highest daily rate is the rate to be used when there's overlap with high/low cost zones
            (LOW_COST_TRAVEL_DAY_RATE * 1)
            + (LOW_COST_FULL_DAY_RATE * 1)
            + (HIGH_COST_TRAVEL_DAY_RATE * 1)
            + (HIGH_COST_FULL_DAY_RATE * 2)
        ),
        high_cost_full_days=2,
        high_cost_travel_days=1,
        low_cost_full_days=1,
        low_cost_travel_days=1,
    )
