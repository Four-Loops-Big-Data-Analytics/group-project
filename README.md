## Big Data Analytics Group Project
### Birkbeck University 2026
### Team: Four Loops

Dan Papier | Marcos Soto | Aidan | Edward Emmett

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
| `reports/validation_report.txt` | Validation results |
| `reports/analytics_report.csv` | Speaking analytics |
| `reports/analytics_report.md` | Analytics in Markdown format |

---

## Stage 1 — Speech Transcription


## Stage 2 — AI Correction

Stage 2 offers two model options:

**Gemini API (serial only):** Calls the Gemini API sequentially with a 5-second delay between requests due to rate limits. Processing 27 rows takes approximately 150 seconds.
Although Gemini is slower due to API rate limits, it produces higher quality corrections than Ollama's local qwen2:7b model, as it is a significantly larger and more capable language model.

**Ollama (serial or parallel):** Uses a local Ollama model (`qwen2:7b`) with no rate limits. Serial processing takes ~20 seconds. Parallel processing using `ThreadPoolExecutor` with 3 workers completes in ~23 seconds. Parallel processing is only viable with Ollama since Gemini's rate limits make concurrent calls impractical. 
We use ThreadPoolExecutor because the Ollama calls are I/O bound — the bottleneck is waiting for the network response, not computation. Threads are more efficient than processes for this type of task because they share memory and have less overhead than spawning separate processes.

## Stage 3 — Data Enrichment
<<<<<<< HEAD
Stage 3 takes the corrected transcript produced in stage 2 and enriches it by adding a set of columns (stats) via Python ensuring reproducibility. This results in data/meeting_enriched.csv. The script relies on csv and os modules using csv.DictReader to parse each row as a dictionary rather than a list. More readable as row["name"] returns the speakers name directly rather than row[0] which would require further digging. If the csv is rearranged, a positional index would silently grab the wrong value. A turn_counter dictionary is used to implement speaker_turn_id, holding a separate count per speaker which tracks their turn. For each row, question_flag checks whether a line ends with a question mark; num_words and text_size_chars use split() and len() and speech_rate_wps is calculated by dividing the word count by time_taken_sec, rounded to 2dps.
=======
>>>>>>> b87927de2daf3feb6e8b57123a4b5d4dd6372e0b


## Stage 4 — Validation


## Stage 5 — Analytics

---

## Complexity Discussion

**Stage 1 (Speech Transcription):** An improved solution could assign multiple threads to calling the Vosk transcription model in parallel.

**Stage 2 (AI correction):** Time complexity is O(N) where N is the number of rows — each row is processed exactly once. Space complexity is O(1) for serial processing since only one row is held in memory at a time. Parallel processing with 3 workers maintains O(N) time complexity but reduces wall-clock time significantly by processing multiple rows concurrently.

<<<<<<< HEAD
**Stage 3 (Data Enrichment):** Time complexity is O(N) where N is the number of rows with each row being processed once in a single pass. Space complexity is also O(N) since all enriched rows are held in the output_rows list before writing. So memory grows in proportion to the number of rows.
=======
**Stage 3 (Data Enrichment):**
>>>>>>> b87927de2daf3feb6e8b57123a4b5d4dd6372e0b


**Stage 4 (Validation):** In stage4.py for example, we attempted to reduce memory usage by streaming the .csv input file line by line and performing all validation checks at once. That is, we only loop through the file once. Log entries and errors are saved to RAM.


**Stage 5 (Analytics):**