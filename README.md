## Big Data Analytics Group Project
### Birkbeck University 2026
### Team: Four Loops

Dan Papier | Marcos Soto | Aidan Ozdural | Edward Emmett

---

## What does the app do?

This project builds a speech analytics pipeline for a simulated startup meeting. It records or loads audio files, transcribes them using the Vosk speech-to-text model, corrects the transcripts using AI, enriches the data with calculated features, validates the dataset, and produces speaking analytics.

The full pipeline runs in sequence:
1. **Stage 1** — Transcribe audio files or live microphone input using Vosk
2. **Stage 2** — Correct transcripts using Gemini API or local Ollama model
3. **Stage 3** — Enrich the dataset with calculated columns
4. **Stage 4** — Validate the dataset
5. **Stage 5** — Analyse speaking patterns and generate reports

---

## Set-up

Download `vosk-model-en-us-0.22-lgraph` from https://alphacephei.com/vosk/models and place it in the project root directory `group-project/`.

Add your `.wav` recordings (16kHz sample rate, mono) to `group-project/recordings/`.
This is the specific file format required by the Vosk transcription model.

If using Gemini, add your API key to a `.env` file in the project root: ```GEMINI_API_KEY="your_key_here"```

If using Ollama, make sure Ollama is running locally before executing the pipeline.

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to run

```bash
python main.py
```

The pipeline will guide you through the options interactively.

---

## What files are produced

| File | Description |
|------|-------------|
| `data/meeting_raw.csv` | Raw Vosk transcriptions |
| `data/meeting_corrected.csv` | AI-corrected transcripts |
| `data/meeting_enriched.csv` | Dataset with calculated features |
| `data/meeting_validated.csv` | Cleaned dataset, with broken rows removed |
| `reports/validation_report.txt` | Validation results |
| `reports/analytics_report.csv` | Speaking analytics |
| `reports/analytics_report.md` | Analytics in Markdown format |


---

## Stage 1 — Speech Transcription

Stage 1 offers two transcription approaches:

**Audio file based transcription (stage1_files.py):** Processes pre-recorded .wav files from the recordings folder. Speaker names are extracted from filenames using the format 01_name.wav, where the number sets the conversation order. 

A parallel version (stage1_files_parallel.py) is also available as an alternative, using ProcessPoolExecutor to transcribe multiple files concurrently.

**Live microphone transcription (stage1_live.py):** Records speech in real time using sounddevice. When prompted, the user types each speaker's name, the speaker talks and presses Ctrl+C to stop the recording for that speaker. Sentences are written to the CSV once the speaker finishes.

Both of these approaches use the vosk-model-en-us-0.22-lgraph model and the output is saved to data/meeting_raw.csv with columns: timestamp, name, raw_text_vosk, time_taken_sec.

**Parallel transcription from files** Spins up multiple processes to run Vosk audio transcription in parallel. Multithreading is not possible in this case, as Vosk is not thread-safe: a separate instance of the model is required for each process. The user is prompted to select their desired number of cores, otherwise a default value (total available cores - 1) is used. I've used .map() to ensure that transcriptions are returned in the correct order. Parallelism should greatly speed up the CPU-heavy transcription process and is recommended, especially since recordings do not need to be transcribed sequentially.

## Stage 2 — AI Correction

Stage 2 offers two model options:

**Gemini API (serial only):** Calls the Gemini API sequentially with a 5-second delay between requests due to rate limits. Processing 27 rows takes approximately 150 seconds.
Although Gemini is slower due to API rate limits, it produces higher quality corrections than Ollama's local qwen2:7b model, as it is a significantly larger and more capable language model.

**Ollama (serial or parallel):** Uses a local Ollama model (`qwen2:7b`) with no rate limits. Serial processing takes ~20 seconds. Parallel processing using `ThreadPoolExecutor` with 3 workers completes in ~23 seconds. Parallel processing is only viable with Ollama since Gemini's rate limits make concurrent calls impractical. 
We use ThreadPoolExecutor because the Ollama calls are I/O bound — the bottleneck is waiting for the network response, not computation. Threads are more efficient than processes for this type of task because they share memory and have less overhead than spawning separate processes.

## Stage 3 — Data Enrichment
Stage 3 takes the corrected transcript produced in stage 2 and enriches it by adding a set of columns (stats) via Python ensuring reproducibility. This results in data/meeting_enriched.csv. The script relies on csv and os modules using csv.DictReader to parse each row as a dictionary rather than a list. More readable as row["name"] returns the speakers name directly rather than row[0] which would require further digging. If the csv is rearranged, a positional index would silently grab the wrong value. A turn_counter dictionary is used to implement speaker_turn_id, holding a separate count per speaker which tracks their turn. For each row, question_flag checks whether a line ends with a question mark; num_words and text_size_chars use split() and len() and speech_rate_wps is calculated by dividing the word count by time_taken_sec, rounded to 2dps.


## Stage 4 — Validation
Validated, complete rows are saved to a new file, while errors are written to validation_report.txt. This ensures that the dataset has 100% density and all data points are valid, before passing it on to analytics. Currently, as the file is small, log entries/errors and cleaned data are stored in RAM and then written to file all at once, which could be an issue given a huge dataset (we could run out of RAM). However, this prevents slow disk write speeds bottle-necking the process. A better solution might yield logs/errors using a generator, then write them to file one at a time (or in batches) in parallel.

## Stage 5 — Analytics
Uses the pandas module to perform data analytics. Results are saved to RAM before being written to a .csv file, and more human-readable .md file. Similarly to Stage 4, could overflow RAM given a large enough dataset as analytics are saved to RAM before bein written to file; a generator approach with parallel file writes may be a better approach.


## Complexity Discussion

**Stage 1 (Speech Transcription):** 

*Audio file based:* Time complexity is O(N × M) where N is the number of audio files and M is the number of frames per file. 
Space complexity is O(S) where S is the total number of sentences.

*Audio file based parallel:* Time complexity is also O(N × M) for the total work but with parallel it is distributed across multiple processes which makes it faster as it reduces CPU clock time. Processes are used instead of threads because Vosk is not thread-safe and requires a separate model instance per worker. 
Space complexity increases as each worker loads its own copy of the Vosk model.

*Live microphone:* Time complexity is O(M) where M is the total frames captured from the microphone. 
Space complexity is O(S) per speaker, as sentences are buffered per speaker and written to CSV after each turn.

**Stage 2 (AI correction):** Time complexity is O(N) where N is the number of rows — each row is processed exactly once. Space complexity is O(1) for serial processing since only one row is held in memory at a time. Parallel processing with 3 workers maintains O(N) time complexity but reduces wall-clock time significantly by processing multiple rows concurrently.

**Stage 3 (Data Enrichment):** Time complexity is O(N) where N is the number of rows with each row being processed once in a single pass. Space complexity is also O(N) since all enriched rows are held in the output_rows list before writing. So memory grows in proportion to the number of rows.

**Stage 4 (Validation):** Memory is O(m + l) where m is the amount of errors detected, plus l being the size of one line of the input csv. Time complexity is (n * l), where l is the number of lines in the input csv, and n the number of columns. I attempted to reduce memory usage by streaming the .csv input file line by line and performing all validation checks at once, thereby looping through the file only once and maintaining O(n * l).

**Stage 5 (Analytics):**
Similarly to Stage 4, this saves analytics results to RAM before writing them to disk, which could be an issue given a large enough dataset. Pandas defaults to using int64 and float64, so memory usage could be optimised by downcasting to smaller numeric types (if the accuracy tradeoff is considered worthwhile). Otherwise pandas is highly optimised using NumPy and contiguous C-arrays; for example, groupby() plus aggregations like sum() is an O(n) operation (it uses hash tables for faster lookups). Space complexity is O(m + n) where m is the input dataset, and n is the output analytics data.

**AI Declaration**
(Aidan)- This project used Claude (Anthropic) to assist with debugging, code development and documentation (stage 3). See AI Declaration for more details 

(Dan) - This project used Claude (Anthropic) to assist with debugging, help understanding other team members code including summarising any changes and documentation.

(Edward) - This project used Google Gemini to assist with debugging, help understanding other team members code including summarising any changes and documentation.