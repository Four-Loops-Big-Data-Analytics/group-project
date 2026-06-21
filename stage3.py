import csv
import os
from config import DATA_DIR
 
OUTPUT_FILE = "data/meeting_enriched.csv"
 
def add_derived_columns(input_rows):
    # Track how many turns each speaker has had so far
    turn_counter = {}
    output_rows = []
 
    for row in input_rows:
        name = row["name"]
        text = row["text"].strip()
        time_taken = float(row["time_taken_sec"])
 
        question_flag = True if text.endswith("?") else False
        num_words = len(text.split())
        text_size_chars = len(text)
        speech_rate_wps = round(num_words / time_taken, 2)
 
        # Increment turn count per speaker independently
        turn_counter[name] = turn_counter.get(name, 0) + 1
        speaker_turn_id = turn_counter[name]
 
        output_rows.append({
            "timestamp":       row["timestamp"],
            "name":            name,
            "raw_text_vosk":   row["raw_text_vosk"],
            "text":            text,
            "time_taken_sec":  time_taken,
            "question_flag":   question_flag,
            "num_words":       num_words,
            "text_size_chars": text_size_chars,
            "speech_rate_wps": speech_rate_wps,
            "speaker_turn_id": speaker_turn_id,
        })
 
    return output_rows
 
def save_to_csv(output_rows):
    os.makedirs("data", exist_ok=True)
    fieldnames = [
        "timestamp", "name", "raw_text_vosk", "text",
        "time_taken_sec", "question_flag", "num_words",
        "text_size_chars", "speech_rate_wps", "speaker_turn_id",
    ]
    # open the file and write all rows
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
 
def enrich_csv(filename):
    INPUT_FILE = DATA_DIR / filename
    if not os.path.exists(INPUT_FILE):
        print(f"Error: '{INPUT_FILE}' not found. Make sure Stage 2 output exists.")
        return
 
    with open(INPUT_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        input_rows = list(reader)
 
    print(f"Loaded {len(input_rows)} rows from '{INPUT_FILE}'.")
 
    output_rows = add_derived_columns(input_rows)
    total = len(output_rows)
    save_to_csv(output_rows)
 
    print(f"Enriched CSV saved to '{OUTPUT_FILE}'.")
    print(f"{total} rows processed.")
    print(f"Columns added: question_flag, num_words, text_size_chars, speech_rate_wps, speaker_turn_id")