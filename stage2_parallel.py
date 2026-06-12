import os
import csv
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import requests


INPUT_FILE = "data/meeting_raw_mock_data.csv"
OUTPUT_FILE = "data/meeting_corrected_mock_data.csv"

MODEL_NAME = "qwen2:7b"
OLLAMA_URL = "http://172.23.128.1:11434/api/generate"


def ask_ollama(transcript):

    prompt = (
        f"""Correct the following transcript. Fix spelling, punctuation, and capitalization only at the start of sentences and for proper nouns.
        NEVER: capitalize every word, change meaning, add content, change words, add quotes, or include explanations.
        OUTPUT: return only the corrected sentence, nothing else.
        Transcript: {transcript}"""
    )
    
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def record_correction_row(correction, line_raw):
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([line_raw["timestamp"], line_raw["name"], line_raw["raw_text_vosk"], correction, line_raw["time_taken_sec"]])


def csv_corrected_heading():
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "raw_text_vosk", "text" ,"time_taken_sec"])


def record_corrected_lines():

    print("Starting correction:")
    start = time.perf_counter()
    print()

    csv_corrected_heading()
    
    with open(INPUT_FILE, encoding="utf-8") as file:
            reader_csv = csv.DictReader(file, delimiter=',')
            rows = list(reader_csv)
            count = 0

            transcripts = [line["raw_text_vosk"] for line in rows]

            with ThreadPoolExecutor(max_workers=3) as executor:
                results = executor.map(ask_ollama, transcripts)
                results_rows = zip(results, rows)

                for result, row in results_rows:
                    count += 1
                    record_correction_row(result, row)
    
    end = time.perf_counter()

    print(f"Process completed, {count} lines corrected succesfully")
    print()
    print(f"Parallel time: {end - start:.2f}s")
    print()
    print("Serial processing takes around 140 secons with gemini due to the rate limit, huge upgrade ...")
    print()



if __name__ == "__main__":

    record_corrected_lines()