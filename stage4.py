# At least 25 rows.
# No required values are missing.
# timestamp values can be parsed as dates/times.

# time_taken_sec is numeric and greater than 0.
# num_words is numeric and greater than 0.
# speech_rate_wps is numeric and greater than 0.
# speaker_turn_id is numeric and greater than 0.

# question_flag contains boolean values.

import csv
from datetime import datetime

ENRICHED_CSV = "data/meeting_enriched.csv"
MIN_ROWS = 25

# check numeric
# if yes cast to int
# if no cast to float
# check greater than 0

def is_numeric_and_greater_than_zero(data):
    if data.strip().isnumeric():
        data = int(data)
    else:
        try:
            data = float(data) 
        except ValueError as error:
            print(f"Error: unable to parse float from {data}.")
            return False
    if data > 0:
        return True
    else: 
        return False

with open(ENRICHED_CSV, "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames or []
    found_missing = False
    row_count = 0

    numeric_fields = ["time_taken_sec", "num_words", "speech_rate_wps", "speaker_turn_id"]

    for line_number, row in enumerate(reader, start=2):

        row_count += 1

        for column in fieldnames:

            value = row[column]
            
            if value is None or value.strip() == "":
                found_missing = True
                print(f"Missing data on line {line_number}, column {column}.")

            if column == "question_flag":
                if not isinstance(value, bool):
                    print(f"Error on line {line_number}, cell {column}: {value} is not a boolean.")
            
            if column in numeric_fields:
                if not is_numeric_and_greater_than_zero(value):
                    print(f"Error on line {line_number}, cell {column}: {value} is not numeric or not greater than zero.")

            if column == "timestamp":
                try:
                    datetime_obj = datetime.fromisoformat(value)
                except ValueError, TypeError:
                    print(f"Unable to parse datetime timestamp from {value} (assuming ISO format).")

    if row_count < MIN_ROWS:
        print(f"CSV contains insufficient rows (less than {MIN_ROWS}).")

    if not found_missing:
        print("No empty cells found.")