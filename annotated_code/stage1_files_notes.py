import json
import csv
import os
import wave
from datetime import datetime, timedelta
from vosk import Model, KaldiRecognizer


MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
SAMPLE_RATE = 16000
RECORDINGS_FOLDER = "recordings"
OUTPUT_FILE = "data/meeting_raw.csv"


def get_speaker_name(filename):
    name = filename.replace(".wav", "").split("_", 1)[1]
    # .split("_", 1) this means 'make only one cut' (even if there are more underscores)
    return name.title()
    # .title() is a built-in function returning title case (capitalises first letter)


def transcribe_file(filepath, model):
    # rb = read only, binary mode (ie 1s and 0s representing a waveform, not chars)
    # wf = wave file
    wf = wave.open(filepath, "rb")

    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    sentences = []
    sentence_start = 0.0

    while True:
        
        data_chunk = wf.readframes(4000)

        if len(data_chunk) == 0:
            break

        current_time_seconds = wf.tell() / SAMPLE_RATE
        # wf.tell() returns current frame number, and there are SAMPLE_RATE frames per second

        # feeds 4000 more frames to vosk at a time
        # model is stateful and remembers everything it's heard so far
        # AcceptWaveform() returns True only when vosk detects a pause (ie, the speaker's phrase is finished)
        if recognizer.AcceptWaveform(data_chunk):
            # converts json into python dictionary
            result = json.loads(recognizer.Result())
            # returns empty string by default
            text = result.get("text", "")

            if text:
                elapsed = round(current_time_seconds - sentence_start, 2)
                sentences.append((text, elapsed))
                sentence_start = current_time_seconds

    # FinalResult() is necessary to flush remainder of file if vosk hasn't heard a pause yet
    # like if the recorder cuts off mid-sentence/without leaving a 'natural pause' at the end
    final_result = json.loads(recognizer.FinalResult())
    final_text = final_result.get("text", "")
    if final_text:
        elapsed = round(current_time_seconds - sentence_start, 2)
        sentences.append((final_text, elapsed))

    wf.close()
    return sentences


def transcribe_from_files():

    recording_files = sorted(os.listdir(RECORDINGS_FOLDER))

    if not recording_files:
        print(f"No files found in '{RECORDINGS_FOLDER}' folder. Please add .wav files and try again.")
        return

    for recording_file in recording_files:
        if not recording_file.endswith(".wav"):
            print(f"Error: '{recording_file}' is not a .wav file. All files must be .wav")
            return

    model = Model(MODEL_PATH)
    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "name", "raw_text_vosk", "time_taken_sec"])
        row_count = 0
        meeting_time = datetime.now()

        for recording_file in recording_files:
            filepath = os.path.join(RECORDINGS_FOLDER, recording_file)
            name = get_speaker_name(recording_file)

            print(f"Processing: {recording_file} (Speaker: {name})")

            sentences = transcribe_file(filepath, model)

            for text, elapsed in sentences:
                timestamp = meeting_time.isoformat(timespec="seconds")
                writer.writerow([timestamp, name, text, elapsed])
                row_count += 1
                print(f"{row_count}: \"{text}\" ({elapsed}s)")
                meeting_time += timedelta(seconds=elapsed)

            print()

    print(f"Meeting finished! {row_count} rows saved.")
    print(f"CSV saved to: {OUTPUT_FILE}")

    if row_count < 25:
        print(f"\nWarning: You have {row_count} row(s) but need at least 25.")

if __name__ == "__main__":
    transcribe_from_files()