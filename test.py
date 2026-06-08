from annotated_code.stage1_files_refactor import transcribe_from_files
from stage2 import record_corrected_lines
from config import DATA_DIR, RECORDINGS_DIR

INPUT_FILE = DATA_DIR / "meeting_raw.csv"
INPUT_MOCK = DATA_DIR / "meeting_raw_mock_data.csv"

if __name__ == "__main__":
    
    transcribe_from_files(RECORDINGS_DIR)

    record_corrected_lines(INPUT_FILE)