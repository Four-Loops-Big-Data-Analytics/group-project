from config import DATA_DIR, REPORTS_DIR
import csv
from datetime import datetime

MIN_ROWS = 25
REPORT_FILE = REPORTS_DIR / "validation_report.txt"
OUTPUT_FILE = DATA_DIR / "meeting_validated.csv"

def is_numeric_and_greater_than_zero(data):
    try:
        return float(data) > 0
    except (ValueError, TypeError):
        return False

def log_and_report(logs_list):
    
    with open(REPORT_FILE, "w", encoding="utf-8") as file:
            
        for log in logs_list:
            print(log)
            file.write(f"{log}\n")

def write_to_csv(output):
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as file:
        ...

def validate_csv(filename):

    print(f"Validating {filename}...")

    with open(DATA_DIR / filename, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        found_missing = False
        row_count = 0
        num_broken_rows = 0
        numeric_fields = ["time_taken_sec", "num_words", "speech_rate_wps", "speaker_turn_id"]
        report_output = []
        valid_output = []

        for line_number, row in enumerate(reader, start=2):

            row_count += 1
            detected_error = False

            for column in fieldnames:

                # if value is None, this defaults to ""
                # avoids potential crashes with None.strip()
                value = (row.get(column) or "").strip()
                
                if not value:
                    found_missing = True
                    detected_error = True
                    report_output.append(f"Missing data on line {line_number}, column {column}.")
                    continue

                if column == "question_flag":
                    if value not in ("True", "False"):
                        detected_error = True
                        report_output.append(f"Error on line {line_number}, cell {column}: {value} is not a boolean.")
                
                if column in numeric_fields:
                    if not is_numeric_and_greater_than_zero(value):
                        detected_error = True
                        report_output.append(f"Error on line {line_number}, cell {column}: {value} is not numeric or not greater than zero.")

                if column == "timestamp":
                    try:
                        datetime.fromisoformat(value)
                    except (ValueError, TypeError):
                        report_output.append(f"Unable to parse datetime timestamp from {value} (assuming ISO format).")
                        detected_error = True

                if detected_error:
                    num_broken_rows += 1
                else:
                    valid_output.append(row)


        if row_count < MIN_ROWS:
            report_output.append(f"CSV contains insufficient rows (less than {MIN_ROWS}).")

        if not report_output:
            print(f"No errors ")

        if not found_missing:
            report_output.append("No empty cells found.")

        log_and_report(report_output)

        print(f"Performed validation of {filename} and saved results to {REPORT_FILE}.")