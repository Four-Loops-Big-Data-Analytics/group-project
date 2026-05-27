import os
from google import genai
import csv
from dotenv import load_dotenv
import time

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# limit to 5 calls per minute and 20 per day
MODEL_NAME_1 = "gemini-2.5-flash"
time_sleep_1 = 13

# limit to 15 calls per minute and 500 per day
MODEL_NAME_2 = "gemini-3.1-flash-lite"
time_sleep_2 = 5

# If you wish to use another model feel free to chage the model name and time sleep varibles uncomenting and filling the following two lines
# MODEL_NAME_3 = 
# time_sleep_3 = 
# This variables are use MODEL_NAME in line 32 and time_sleep in line 65, change them with the new variables



def ask_gemini(transcript):
    prompt = (
        f"""As an expert corrector your job is to correct the following transcript: {transcript}. 
        MUST: add the proper notation, capitals or anythIng that is needed to be perfect. 
        NEVER: change the meaning of the transcript, add new content, change the content or change any word.
        OUTPUT: return only the corrected transcript, no explanations, no preamble."""
        )
    response = client.models.generate_content(model=MODEL_NAME_2, contents=prompt)
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
    
    with open("data/meeting_raw_mock_data.csv", encoding="utf-8") as file:
            reader_csv = csv.DictReader(file, delimiter=',')
            count = 1
            corrected_lines = 0
            for line in reader_csv:
                try:
                    print(f"Correcting line {count}")
                    correct_transcript = ask_gemini(line["raw_text_vosk"])
                    record_correction_row(correct_transcript, line)
                    print(f"Line {count} corrected succesfully")
                    corrected_lines += 1
                except Exception as e:
                    print(f"Error on row: {count}, line not corrected")
                    record_correction_row(line["raw_text_vosk"], line)
                count += 1
                # Had to set a timer for the calls per minute
                time.sleep(time_sleep_2)
    print(f"Process completed, {corrected_lines} lines corrected succesfully")
