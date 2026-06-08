import json
import csv
import os
import wave
from datetime import datetime, timedelta
from vosk import Model, KaldiRecognizer
from config import RECORDINGS_DIR, DATA_DIR
from pathlib import Path

MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
SAMPLE_RATE = 16000
OUTPUT_FILE = DATA_DIR / "meeting_raw.csv"

def get_speaker_name(filename):
    name = filename.replace(".wav", "").split("_", 1)[1]
    return name.title()

def transcribe_file(filepath, model):
    wf = wave.open(str(filepath), "rb")

    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    sentences = []
    sentence_start = 0.0

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
                sentences.append((text, elapsed))
                sentence_start = current_time_seconds

    final_result = json.loads(recognizer.FinalResult())
    final_text = final_result.get("text", "")
    if final_text:
        elapsed = round(current_time_seconds - sentence_start, 2)
        sentences.append((final_text, elapsed))

    wf.close()
    return sentences

def transcribe_from_files(folder: Path):

    recording_files = sorted(os.listdir(folder))

    if not recording_files:
        print(f"No files found in '{folder.name}' folder. Please add .wav files and try again.")
        return
    
    for recording_file in recording_files:
        if not recording_file.endswith(".wav"):
            print(f"Error: '{recording_file}' is not a .wav file. All files must be .wav")
            return

    model = Model(MODEL_PATH)
    row_count = 0
    meeting_time = datetime.now()
    output = []

    for recording_file in recording_files:

        filepath = RECORDINGS_DIR / recording_file
        name = get_speaker_name(recording_file)

        print(f"Processing: {recording_file} (Speaker: {name})")

        sentences = transcribe_file(filepath, model)

        for text, elapsed in sentences:
            timestamp = meeting_time.isoformat(timespec="seconds")
            output.append({
                "timestamp":timestamp,
                 "name":name, 
                 "raw_text_vosk":text, 
                 "time_taken_sec":elapsed
                })
            
            row_count += 1

            print(f"{row_count}: \"{text}\" ({elapsed}s)")

            meeting_time += timedelta(seconds=elapsed)

        print()

    HEADERS = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]

    # dump data all at once
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=HEADERS)
        writer.writeheader()
        if output:
            writer.writerows(output)
        else:
            print("Error: no output generated.")

    print(f"All recordings saved! {row_count} rows saved.")
    print(f"CSV saved to: {OUTPUT_FILE}")

    if row_count < 25:
        print(f"\nWarning: You have {row_count} row(s) but need at least 25.")