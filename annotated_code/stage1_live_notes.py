import json
import queue
import time
import csv
import os
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-en-us-0.22-lgraph"

# 16kHz sample rate, standard for VoIP
# 16kHz accurately captures up to 8kHz frequency range; human voice is 300 - 3400 kHz
# keeps files small
SAMPLE_RATE = 16000
OUTPUT_FILE = "data/meeting_raw.csv"

# thread-safe queue; mic dumps data to the queue to then be processed by model
q = queue.Queue()

# sounddevice library expects four positional args:
# indata: raw audio data that was just captured
# frames: number of frames in this chunk. not used in this case
# time_info: dictionary containing timing info. not used in this case
# status: error flag
def callback(indata, frames, time_info, status):

    # status is empty if everything ok, otherwise prints error
    if status:
        print(status)

    # converts (NumPy?) array to raw stream of bytes
    q.put(bytes(indata))


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

            if name == "quit":
                if row_count < 25:
                    print(f"\nWarning: You have {row_count} row(s) but need at least 25.")
                    confirm = input("Are you sure you want to quit? (yes/no):").strip().lower()
                    if confirm != "yes":
                        continue
                break

            if name == "":
                print("Name is blank. Please enter speaker name (or 'quit' to finish): .\n")
                continue

            recognizer = KaldiRecognizer(model, SAMPLE_RATE)

            sentence_start = time.perf_counter()

            print(f"\nRecording {name}. Please speak now.")
            print("Press Ctrl+C to stop this speaker.\n")

            try:

                with sd.RawInputStream(
                    samplerate=SAMPLE_RATE,

                    # 8000 frames = half a second
                    blocksize=8000,

                    # standard 16-bit audio format
                    dtype="int16",

                    # mono
                    channels=1,

                    # triggers callback function every 8000 frames to dump data to the queue
                    callback=callback,
                ):
                    while True:

                        data = q.get()

                        # returns True only when a natural pause or silence is detected
                        if recognizer.AcceptWaveform(data):

                            # converts result JSON into Python dictionary
                            result = json.loads(recognizer.Result())

                            # safety net: text = "" by default
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