import os
import sys

from pathlib import Path
from typing import List

from . import processor


def run(_filename: str) -> int:
    """

    :param _filename:
    :return:
    """
    data = processor.get_data_from_csv(Path(_filename))
    result = processor.process_data(data)

    print(f'Total: ${result.total:.2f}')
    print(f'High Cost Full Days: {result.high_cost_full_days}')
    print(f'High Cost Travel Days: {result.high_cost_travel_days}')
    print(f'Low Cost Full Days: {result.low_cost_full_days}')
    print(f'Low Cost Travel Days: {result.low_cost_travel_days}')
    return 0


def main(args: List[str]) -> int:
    """

    :param args:
    :return:
    """
    if len(args) != 2:
        print("Usage: python -m wb_st_challenge <filename>")
        return 1

    filename = args[1]

    if not (os.path.exists(filename) and os.path.isfile(filename)):
        print(f"Error: File '{filename}' does not exist or else is not a file.")
        return 1

    return run(filename)


if __name__ == '__main__':
    # Note: this line is excluded from coverage b/c it's annoyingly hard to test 🤷🤣
    sys.exit(main(sys.argv))
