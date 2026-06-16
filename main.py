from stage1_files import transcribe_from_files
from stage1_live import record_and_transcribe
from stage2_gemini import record_corrected_lines_gemini
from stage2_ollama import record_corrected_lines_ollama_parallel, record_corrected_lines_ollama_serial
from stage3 import enrich_csv
from stage4 import validate_csv
from stage5 import analyse_csv
from config import RECORDINGS_DIR

if __name__ == "__main__":
    
    print("\nWelcome to the Meeting Speech Analytics with Vosk + AI pipeline!")
    print("\n1. Transcribe from audio files (place .wav files in recordings folder)")
    print("2. Record live meeting from microphone")
    
    # This loop prompts the user to choose between transcribing from files or recording live
    # It continues to prompt for an option of the two until a valid option is made.

    while True:
        option = input("\nChoose an option (1 or 2): ").strip()

        if option == "1":
            transcribe_from_files(RECORDINGS_DIR)
            break
        elif option == "2":
            record_and_transcribe(RECORDINGS_DIR)
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    print()
    print("Stage 2, correction process:")
    print()
    print("There are two model options, Gemini and Ollama")
    print("Gemini is slower due to the api call limits")
    print("Ollama is faster, you can choose between parallel or serial processing")
    print()

    while True:

        model = input("If you want to use Gemini enter g, else if you prefer Ollama enter o: ")

        if model == "g":
            record_corrected_lines_gemini()
            break

        elif model == "o":
            processing = input("If you want parallel processing enter p, else for serial enter s: ")

            if processing == "p":
                record_corrected_lines_ollama_parallel()
                break
            elif processing == "s":
                record_corrected_lines_ollama_serial()
                break
            else:
                print("Invalid choice. Please enter p or s.")
                break
        else:
            print("Invalid choice. Please enter g or o.")

    enrich_csv("meeting_corrected.csv")

    validate_csv("meeting_enriched.csv")

    analyse_csv("meeting_enriched.csv")