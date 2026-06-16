from stage1_files import get_speaker_name
from pathlib import Path
import json
import csv
import wave
from datetime import datetime, timedelta
from vosk import Model, KaldiRecognizer
from config import DATA_DIR, MODEL_PATH
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

SAMPLE_RATE = 16000
OUTPUT_FILE = DATA_DIR / "meeting_raw.csv"
worker_model = None

# recommended: one less than cores on your computer
MAX_WORKERS = 7

# ProcessPoolExecutor uses this to spin up one Model per process
def init_worker(filepath: Path):
    global worker_model
    worker_model = Model(str(filepath))

# grabs name from file and returns it as part of tuple (name, text, elapsed)
def transcribe_file_parallel(filepath):

    global worker_model
    wf = wave.open(str(filepath), "rb")
    recognizer = KaldiRecognizer(worker_model, SAMPLE_RATE)
    sentences = []
    sentence_start = 0.0
    name = get_speaker_name(str(filepath))

    print(f"Transcribing file {filepath}...")

    while True:
        
        data_chunk = wf.readframes(4000)

        if len(data_chunk) == 0:
            break

        current_time_seconds = wf.tell() / SAMPLE_RATE

        if recognizer.AcceptWaveform(data_chunk):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")

            if text:
                elapsed = round(current_time_seconds - sentence_start, 2)
                sentences.append((name, text, elapsed))
                sentence_start = current_time_seconds

    final_result = json.loads(recognizer.FinalResult())
    final_text = final_result.get("text", "")
    if final_text:
        elapsed = round(current_time_seconds - sentence_start, 2)
        sentences.append((name, final_text, elapsed))

    wf.close()
    return sentences

def transcribe_dir_parallel(folder: Path):

    if not folder.exists() or not folder.is_dir():
        print(f"No directory found at {folder}. Please try again.")
        return
    
    if not any(folder.iterdir()):
        print(f"Directory {folder} is empty. Please try again.")
        return
    
    results = []
    wav_files = sorted(
        file for file in folder.iterdir() 
        if file.is_file() 
        and file.suffix.lower() == '.wav'
    )

    with ProcessPoolExecutor(
        max_workers=MAX_WORKERS,
        initializer=init_worker,
        initargs=(MODEL_PATH,)
    ) as executor:
        
        #.map() returns generator in same order as input (ie, sorted .wav files)
        for sentence in executor.map(transcribe_file_parallel, wav_files):
            results.extend(sentence)
        
    write_results_to_file(results)

# calculates timestamp per recording, then writes all results to meeting_raw.csv 
def write_results_to_file(results):

    output = []
    meeting_time = datetime.now()

    for row, (name, text, elapsed) in enumerate(results, start=1):

        timestamp = meeting_time.isoformat(timespec="seconds")

        output.append({
            "timestamp":timestamp,
                "name":name, 
                "raw_text_vosk":text, 
                "time_taken_sec":elapsed
            })
        
        print(f"{row}: \"{text}\" ({elapsed}s)")

        meeting_time += timedelta(seconds=elapsed)

    print()

    HEADERS = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=HEADERS)
        writer.writeheader()
        if output:
            writer.writerows(output)
        else:
            print("Error: no output generated.")

    print(f"All recordings saved! {row} rows saved.")
    print(f"CSV saved to: {OUTPUT_FILE}")

    if row < 25:
        print(f"\nWarning: You have {row} row(s) but need at least 25.")