# WB ST Challenge

This is a tool that will calculate the total reimbursement amount for a set of dates and cost zones, based upon a specific set of rules:

- Any given day is only ever reimbursed once, even if multiple projects are on the same day.
- Projects that are contiguous or overlap, with no gap between the end of one and the start of the next, are considered a sequence of projects and should be treated similar to a single project.
- First day and last day of a project (or sequence of projects) are travel days.
- Any day in the middle of a project (or sequence of projects) is considered a full day.
- If there is a gap between projects, those gap days are not reimbursed and the days on either side of that gap are travel days.
- A travel day is reimbursed at a rate of 45 dollars per day in a low cost city.
- A travel day is reimbursed at a rate of 55 dollars per day in a high cost city.
- A full day is reimbursed at a rate of 75 dollars per day in a low cost city.
- A full day is reimbursed at a rate of 85 dollars per day in a high cost city.

## Installation:

Prerequisites: Python 3.9, 3.10, and/or Python 3.11. Ideally you've got `tox` installed and all three of those versions available.

    git clone https://github.com/wesbroadway/wb-st-challenge.git
    cd wb-st-challenge

## Usage instructions:

To use whichever old version of Python you've got (which should be fine!), you can run it like this:

**Bash:**

    $ python -m wb_st_challenge <data_file.csv>

**Python:**

Or from within a python application, you can do this:

    from wb_st_challenge import processor

    data = processor.get_data_from_csv('/path/to/data_file.csv')
    result = processor.process_data(data)
    
    print(f'Total reimbursement amount: ${result.total:.2f}')
    print(f'Low-cost travel days: {result.low_cost_travel_days}')
    print(f'Low-cost full days: {result.low_cost_full_days}')
    print(f'High-cost travel days: {result.high_cost_travel_days}')
    print(f'High-cost full days: {result.high_cost_full_days}')

You can also submit a list of dicts to `processor.process_data` if your data is not coming from a CSV. See the [docstring](./wb_st_challenge/processor.py#L85) for details.

**Running tests:**

This project uses `tox`, so the recommended way to run the tests is by simply running it from the command line. A coverage report will be displayed, and also an HTML version will be generated in the `./tmp/coverage` directory:

    $ tox
      py39-test: commands succeeded
      py310-test: commands succeeded
      py311-test: commands succeeded
      lint: commands succeeded
      coverage: commands succeeded
      congratulations :)

You can run individual test environments like so:

    $ tox -e py39-test
    $ tox -e lint

If you are running this in your IDE, then you should Python's `unittest` module like so:

    $ python -m unittest discover tests -t .

## Data file structure

The data file should have a header row and three columns:

- start_date: `YYYY-mm-dd`
- end_date: `YYYY-mm-dd`
- cost_zone: "low", "high"

See the example file in this repo for reference: [`data_file_example.csv`](./data_file_example.csv)  
