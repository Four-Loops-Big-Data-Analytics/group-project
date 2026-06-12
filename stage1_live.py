import json
import queue
import time
import csv
import os
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pathlib import Path
from config import DATA_DIR, MODEL_PATH

OUTPUT_FILE = DATA_DIR / "meeting_raw.csv"
SAMPLE_RATE = 16000

q = queue.Queue()

def callback(indata, frames, time_info, status):

    if status:
        print(status)
    q.put(bytes(indata))


def record_and_transcribe():

    model = Model(MODEL_PATH)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "name", "raw_text_vosk", "time_taken_sec"])
        
    row_count = 0

    while True:

        # reprints every time speaker changes (as a reminder to user)
        print("MEETING RECORDER")
        print("\n1. Type your name when prompted")
        print("2. Say your phrase into the microphone")
        print("3. Each sentence is saved automatically")
        print("4. Press Ctrl+C when you're done speaking")
        print("5. Type 'quit' when the meeting is over\n")

        name = input("\nSpeaker name (or 'quit' to finish): ").strip()

        if name.lower() == "quit":
            if row_count < 25:
                print(f"\nWarning: You have {row_count} row(s) but need at least 25.")
                confirm = input("Are you sure you want to quit? (yes/no): ").strip().lower()
                if confirm != "yes":
                    continue
            break

        if not name:
            print("Name is blank. Please enter speaker name.\n")
            continue

        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        sentence_start = time.perf_counter()
        
        # transcribed sentences go in a list in format [timestamp, name, text, elapsed]
        speaker_buffer = []

        print(f"\nRecording {name}. Please speak now.")
        print("Press Ctrl+C to stop this speaker.\n")

        try:
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                while True:
                    data = q.get()

                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "")

                        if text:
                            elapsed = round(time.perf_counter() - sentence_start, 2)
                            timestamp = datetime.now().isoformat(timespec="seconds")
                            
                            # save to speaker_buffer, not to file
                            speaker_buffer.append([timestamp, name, text, elapsed])
                            
                            row_count += 1
                            print(f"{row_count}: \"{text}\" ({elapsed}s)")
                            sentence_start = time.perf_counter()

        except KeyboardInterrupt:
            print(f"\nStopped recording {name}.")
            
            if speaker_buffer:

                # appends phrases to file only when speaker is finished
                with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerows(speaker_buffer)
                print(f"Successfully saved {len(speaker_buffer)} sentences to disk.")
                
            pass

    print(f"\nMeeting finished! {row_count} rows saved.")
    print(f"CSV saved to: {OUTPUT_FILE}")