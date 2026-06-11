from config import DATA_DIR, REPORTS_DIR
import csv
from datetime import datetime

MIN_ROWS = 25
REPORT_FILE = REPORTS_DIR / "validation_report.txt"

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


def validate_csv(filename):

    with open(DATA_DIR / filename, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        found_missing = False
        row_count = 0
        numeric_fields = ["time_taken_sec", "num_words", "speech_rate_wps", "speaker_turn_id"]
        report_output = []

        for line_number, row in enumerate(reader, start=2):

            row_count += 1

            for column in fieldnames:

                value = row[column].strip()
                
                if value is None or value == "":
                    found_missing = True
                    report_output.append(f"Missing data on line {line_number}, column {column}.")

                if column == "question_flag":
                    if value not in ("True", "False"):
                        report_output.append(f"Error on line {line_number}, cell {column}: {value} is not a boolean.")
                
                if column in numeric_fields:
                    if not is_numeric_and_greater_than_zero(value):
                        report_output.append(f"Error on line {line_number}, cell {column}: {value} is not numeric or not greater than zero.")

                if column == "timestamp":
                    try:
                        datetime.fromisoformat(value)
                    except (ValueError, TypeError):
                        report_output.append(f"Unable to parse datetime timestamp from {value} (assuming ISO format).")

        if row_count < MIN_ROWS:
            report_output.append(f"CSV contains insufficient rows (less than {MIN_ROWS}).")

        if not found_missing:
            report_output.append("No empty cells found.")

        log_and_report(report_output)