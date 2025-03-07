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

## Usage instructions:

**Bash:**

    $ python -m wb_st_challenge <data_file.csv>

**Python:**

    from wb_st_challenge import processor
    
    with open('/path/to/data_file.csv', 'r') as f:
        result = processor.process_csv_file(f)
    
    print(f'Total reimbursement amount: ${result.total:.2f}')
    print(f'Low-cost travel days: {result.low_cost_travel_days}')
    print(f'Low-cost full days: {result.low_cost_full_days}')
    print(f'High-cost travel days: {result.high_cost_travel_days}')
    print(f'High-cost full days: {result.high_cost_full_days}')

**Running tests:**

    python -m unittest tests/test_processor.py

## Data file structure

The data file should have three columns:

- Start date: `YYYY-mm-dd`
- End date: `YYYY-mm-dd`
- Cost zone: "low", "high"

See the example file in this repo for reference: [`data_file_example.csv`](./data_file_example.csv)  
