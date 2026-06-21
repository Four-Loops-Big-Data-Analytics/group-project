import os
import csv
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import requests 
from config import DATA_DIR

OUTPUT_FILE = DATA_DIR / "meeting_corrected.csv"

MODEL_NAME = "qwen2:7b"
OLLAMA_URL = "http://172.23.128.1:11434/api/generate"

# Edward's url:
# OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_ollama(transcript):

    prompt = (
        f"""Correct only punctuation and obvious speech-to-text errors in this sentence. 
Do not change, add, or remove any words unless they are clearly a phonetic mishearing. 
Use standard sentence capitalisation only. 
Return only the corrected sentence with no quotes or explanation.
{transcript}"""
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


def record_corrected_lines_ollama_parallel(filename):

    INPUT_FILE = DATA_DIR / filename
    print("Starting parallel correction wth Ollama:")
    print()

    start = time.perf_counter()

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

    print(f"Process completed, {count} lines corrected successfully")
    print()
    print(f"Parallel processing time with ollama: {end - start:.2f}s")
    print()


def record_corrected_lines_ollama_serial(filename):
    
    INPUT_FILE = DATA_DIR / filename

    print("Starting serial correction with Ollama:")
    print()
    
    start = time.perf_counter()

    csv_corrected_heading()
    
    with open(INPUT_FILE, encoding="utf-8") as file:
            reader_csv = csv.DictReader(file, delimiter=',')
            count = 1
            corrected_lines = 0

            for line in reader_csv:

                try:
                    print(f"Correcting line {count}")
                    correct_transcript = ask_ollama(line["raw_text_vosk"])
                    record_correction_row(correct_transcript, line)
                    print(f"Line {count} corrected successfully")
                    corrected_lines += 1

                except Exception as e:
                    print(f"Error on row: {count}: {e}, line not corrected")
                    record_correction_row(line["raw_text_vosk"], line)

                print()
                count += 1

    end = time.perf_counter()  

    print(f"Process completed, {corrected_lines} lines corrected successfully")
    print()
    print(f"Serial processing time with ollama: {end - start:.2f}s")
    print()