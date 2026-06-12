# What is the average speaking time per speaker?
# What is each speaker's average speech rate?

import pandas
import csv
from config import DATA_DIR, REPORTS_DIR
OUTPUT_FILE = REPORTS_DIR / "analytics_report.csv"

def analyse_csv(filename):

    output = []

    df = pandas.read_csv(DATA_DIR / filename)

    words_per_speaker = df.groupby('name')['num_words'].sum()
    top_speaker = words_per_speaker.idxmax()
    max_words = words_per_speaker.max()
    min_speaker = words_per_speaker.idxmin()
    min_words = words_per_speaker.min()

    questions_per_speaker = df.groupby('name')['question_flag'].sum()
    top_questioner = questions_per_speaker.idxmax()
    max_questions = questions_per_speaker.max()

    total_time = df['time_taken_sec'].sum()

    for row in [
        {"Metric":"Most words spoken", "Result":f"{top_speaker}, {max_words} words"},
        {"Metric":"Least words spoken", "Result":f"{min_speaker}, {min_words} words"},
        {"Metric":"Most questions", "Result":f"{top_questioner}, {max_questions} question(s)"},
        {"Metric":"Total speaking time", "Result":f"{total_time} sec(s)"}
        ]:
        output.append(row)

    avg_time_per_speaker = df.groupby('name')['time_taken_sec'].mean().round(2).sort_values(ascending=False)

    avg_wps_per_speaker = df.groupby('name')['speech_rate_wps'].mean().round(2).sort_values(ascending=False)

    for (speaker, avg) in avg_time_per_speaker.items():
        output.append(
            {"Metric":f"Average speaking time", "Result":f"{speaker}, {avg} sec(s)"}
        )

    for (speaker, wps) in avg_wps_per_speaker.items():
        output.append(
            {"Metric":f"Average speech rate", "Result":f"{speaker}, {wps} words/second"}
        )
    
    time_per_speaker = df.groupby('name')['time_taken_sec'].sum().sort_values(ascending=False)

    for i, (speaker, time) in enumerate(time_per_speaker.head().items(), start=1):
        output.append(
            {"Metric":f"Total speaking time, rank {i}", "Result":f"{speaker}, {time} sec(s)"}
        )

    generate_report(output)
    
def generate_report(output_list):
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as file:
        headers = ["Metric", "Result"]
        writer = csv.DictWriter(file, headers)
        writer.writeheader()
        writer.writerows(output_list)