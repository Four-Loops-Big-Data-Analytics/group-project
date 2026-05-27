import os
from google import genai
import csv
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL_NAME = "gemini-2.5-flash"


def ask_gemini(transcript):
    prompt = (
        f"""As an expert corrector your job is to correct the following transcript: {transcript}. 
        MUST: add the proper notation, capitals or anythIng that is needed to be perfect. 
        NEVER: change the meaning of the transcript, add new content or change the content 
        OUTPUT: return only the corrected transcript, no explanations, no preamble."""
        )
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text

def record_correction_row(correction, line_raw):
    with open("data/meeting_corrected.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([line_raw["timestamp"], line_raw["name"], line_raw["raw_text_vosk"], correction, line_raw["time_taken_sec"]])

def csv_corrected_heading():
    with open("data/meeting_corrected.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "raw_text_vosk", "text" ,"time_taken_sec"])

def record_corrected_lines():

    csv_corrected_heading()
    
    with open("data/meeting_raw.csv", encoding="utf-8") as file:
            reader_csv = csv.DictReader(file, delimiter=',')
            for line in reader_csv:
                try:
                    correct_transcript = ask_gemini(line["raw_text_vosk"])
                    record_correction_row(correct_transcript, line)
                except Exception as e:
                    print(f"Error on row: {e}")
                    record_correction_row(line["raw_text_vosk"], line)