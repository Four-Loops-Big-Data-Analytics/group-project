import json
import queue
import time
import csv
import os
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Vosk model path and audio settings
MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
SAMPLE_RATE = 16000

# File path for raw file output
OUTPUT_FILE = "data/meeting_raw.csv"

# Queue to pass audio data from the microphone callback to the main loop for processing with Vosk.
q = queue.Queue()

# Called for each audio chunk captured from the microphone.
# Puts each audio data into a queue for processing in the main loop
def callback(indata, frames, time_info, status):
    if status:
        print(status)
    q.put(bytes(indata))

# Records live speech from the microphone, transcribes it with Vosk and saves the raw data to a csv file.
def record_and_transcribe():
    model = Model(MODEL_PATH)
    os.makedirs("data", exist_ok=True)


    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "raw_text_vosk", "time_taken_sec"])
        row_count = 0

        print("MEETING RECORDER")
        print()
        print("1. Type your name when prompted")
        print("2. Say your phrase into the microphone")
        print("3. Each sentence is saved automatically")
        print("4. Press Ctrl+C when you're done speaking")
        print("5. Type 'quit' when the meeting is over")
        print()


        while True:
            name = input("\nSpeaker name (or 'quit' to finish): ").strip()

            # If the user types "quit", this checks if they have at least 25 rows and prompts for confirmation if not before breaking the loop to finish the meeting.
            if name == "quit":
                if row_count < 25:
                    print(f"\nWarning: You have {row_count} row(s) but need at least 25.")
                    confirm = input("Are you sure you want to end the meeting? (yes/no):").strip().lower()
                    if confirm != "yes":
                        continue
                break

            # If the user leaves the name blank, this prompts them to enter a name before continuing.
            if name == "":
                print("Name is blank.Please enter speaker name (or 'quit' to finish): .\n")
                continue

            # Creates a new Vosk recognizer for each speaker to reset the state and avoid audio interference between speakers.
            recognizer = KaldiRecognizer(model, SAMPLE_RATE)

            sentence_start = time.perf_counter()

            print(f"\nRecording {name}. Please speak now.")
            print("Press Ctrl+C to stop this speaker.\n")

            # Catches Ctrl+C to stop recording the current speaker without stopping the script.
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
                                writer.writerow([timestamp, name, text, elapsed])
                                row_count += 1
                                print(f"{row_count}: \"{text}\" ({elapsed}s)")
                                sentence_start = time.perf_counter()

            except KeyboardInterrupt:
                print(f"\nStopped recording {name}.")
                pass

    print(f"\nMeeting finished! {row_count} rows saved.")
    print(f"CSV saved to: {OUTPUT_FILE}")
