"""

"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from .constants import (
    HIGH_COST_FULL_DAY_RATE,
    HIGH_COST_TRAVEL_DAY_RATE,
    LOW_COST_FULL_DAY_RATE,
    LOW_COST_TRAVEL_DAY_RATE,
)


@dataclass
class ReimbursementResult:
    total: int = 0
    high_cost_full_days: int = 0
    high_cost_travel_days: int = 0
    low_cost_full_days: int = 0
    low_cost_travel_days: int = 0


def parse_date(date_str: str) -> datetime.date:
    """Convert a date string (YYYY-MM-DD) to a datetime.date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_data_into_list_of_projects(data: list) -> list:
    """

    :param data:
    :return:
    """
    projects = [(parse_date(p["start_date"]), parse_date(p["end_date"]), p["cost_zone"]) for p in data]
    projects.sort()
    return projects


def merge_projects(projects: list) -> list:
    """
    Merges projects that have contiguous or overalpping dates, but only if the cost zone is the same.
    :param projects: a list of (start_date, end_date, cost_zone) tuples
    :return:
    """
    merged = []
    for start, end, cost_zone in projects:
        # If the end date of the most recent entry is >= the day before this project's start date, then proceed...
        if merged and merged[-1][1] >= start - timedelta(days=1):
            # Is the cost zone the same?
            if merged[-1][2] == cost_zone:
                # Recreate the most recent entry, and extend the end date
                merged[-1] = (
                    merged[-1][0],  # <-- Keep original start date
                    max(merged[-1][1], end),  # <-- Extend end date
                    cost_zone,  # <-- Keep same cost zone
                )
            else:
                # Cost zone differs / Check if it's fully contained
                if start >= merged[-1][0] and end <= merged[-1][1]:
                    continue  # Skip this entry, as it’s fully inside a larger project

                # Otherwise, keep separate
                merged.append((start, end, cost_zone))
        else:
            # The previous entry's end_date is earlier than the day before this project's start date.
            merged.append((start, end, cost_zone))

    return merged


def process_data(data: list) -> ReimbursementResult:
    """
    Processes a list of projects and calculates reimbursement totals.

    :param data: List of project dictionaries with start_date, end_date, and cost_zone.
    :return: A ReimbursementResult containing the total reimbursement and categorized day counts.
    """
    if not data:
        return ReimbursementResult()

    projects = parse_data_into_list_of_projects(data)
    merged = merge_projects(projects)
    daily_rates = calculate_daily_rates(merged)
    return calculate_reimbursement_result(daily_rates)


def calculate_daily_rates(merged: list) -> dict:
    """
    Calculates daily rates for the merged project list.

    :param merged: List of merged projects
    :return: Dictionary of daily rates {date: (rate, cost_zone, is_travel_day)}
    """
    daily_rates = {}  # { date: (rate, cost_zone, is_travel_day) }

    for index, (start, end, cost_zone) in enumerate(merged):
        current = start
        is_travel_day_tester = make_is_travel_day_tester(merged, index, start, end)

        while current <= end:
            is_travel_day = is_travel_day_tester(current)

            rate = (
                # Disabling Black for this block, this is more readable
                # fmt: off
                HIGH_COST_TRAVEL_DAY_RATE if cost_zone == "high" and is_travel_day else
                LOW_COST_TRAVEL_DAY_RATE if cost_zone == "low" and is_travel_day else
                HIGH_COST_FULL_DAY_RATE if cost_zone == "high" else
                LOW_COST_FULL_DAY_RATE
                # fmt: on
            )

            if current in daily_rates:
                existing_rate, existing_cost_zone, existing_is_travel = daily_rates[current]

                # Ensure high-cost is prioritized over low-cost
                if cost_zone == "high" and existing_cost_zone == "low":
                    daily_rates[current] = (rate, cost_zone, is_travel_day)

                # Keep the highest rate, prioritizing full days over travel days
                elif rate > existing_rate or (rate == existing_rate and not is_travel_day):
                    daily_rates[current] = (rate, cost_zone, is_travel_day)
                else:
                    pass

            else:
                daily_rates[current] = (rate, cost_zone, is_travel_day)

            current += timedelta(days=1)

    return daily_rates


def make_is_travel_day_tester(merged: list, index: int, start: datetime, end: datetime) -> callable:
    """
    Returns a function that determines if a given day is a travel day.

    :param merged: The list of merged projects
    :param index: The current index in the merged list
    :param start: The start date of the current project
    :param end: The end date of the current project
    :return: A function that takes a date and returns True if it's a travel day
    """

    def func(current: datetime) -> bool:
        """
        Determines if a given day is a travel day.

        :param current: The date being checked
        :return: True if the day is a travel day, otherwise False
        """
        return (
            # True start (first day of a sequence)
            (current == start and (index == 0 or merged[index - 1][1] < start - timedelta(days=1)))
            or
            # True end (last day of a sequence)
            (current == end and (index == len(merged) - 1 or merged[index + 1][0] > end + timedelta(days=1)))
        )

    return func


def calculate_reimbursement_result(daily_rates: dict) -> ReimbursementResult:
    """
    Calculates reimbursement total and categorized day counts.
    :param daily_rates:
    :return:
    """
    reimbursement = ReimbursementResult()

    for day, (rate, cost_zone, is_travel_day) in daily_rates.items():
        reimbursement.total += rate
        if cost_zone == "high":
            if is_travel_day:
                reimbursement.high_cost_travel_days += 1
            else:
                reimbursement.high_cost_full_days += 1
        else:
            if is_travel_day:
                reimbursement.low_cost_travel_days += 1
            else:
                reimbursement.low_cost_full_days += 1

    return reimbursement
