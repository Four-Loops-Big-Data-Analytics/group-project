# Who spoke the most by total words?
# Who spoke the least by total words?
# What is the total speaking time of the meeting?
# What is the average speaking time per speaker?
# Who asked the most questions?
# Who are the top 5 speakers by total speaking time?
# What is each speaker's average speech rate?

import pandas
from config import DATA_DIR, REPORTS_DIR


def analyse_csv(filename):

    df = pandas.read_csv(DATA_DIR / filename)

    words_per_speaker = df.groupby('name')['num_words'].sum()

    top_speaker = words_per_speaker.idxmax()

    min_speaker = words_per_speaker.idxmin()

    max_words = words_per_speaker.max()

    time_per_speaker = df.groupby('name')['time_taken_sec'].sum()

    print(df.to_string())


    print(words_per_speaker)
    print(type(words_per_speaker))
    print(top_speaker)
    print(min_speaker)
    print(max_words)
    print(time_per_speaker)
    # top_speaker = df.groupby('')