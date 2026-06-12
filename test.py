from stage1_files import transcribe_from_files
from stage2 import record_corrected_lines
from stage3 import enrich_csv
from stage4 import validate_csv
from stage5 import analyse_csv
from config import RECORDINGS_DIR

if __name__ == "__main__":
    
    transcribe_from_files(RECORDINGS_DIR)

    record_corrected_lines("meeting_raw.csv")

    enrich_csv("meeting_corrected.csv")

    validate_csv("meeting_enriched.csv")

    analyse_csv("meeting_enriched.csv")