from ast import While

from stage1_files import transcribe_from_files
from stage1_live import record_and_transcribe
from stage2 import record_corrected_lines
from stage3 import main as enrich
# from stage4 import main as validate_and_analyse

if __name__ == "__main__":

    print("\nWelcome to the Meeting Speech Analytics with Vosk + AI pipeline!")
    print("\n1. Transcribe from audio files (place .wav files in recordings folder)")
    print("2. Record live meeting from microphone")
    
    # This loop prompts the user to choose between transcribing from files or recording live
    # It continues to prompt for an option of the two until a valid option is made.
    while True:
        option = input("\nChoose an option (1 or 2): ").strip()

        if option == "1":
            transcribe_from_files()
            break
        elif option == "2":
            record_and_transcribe()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    record_corrected_lines()
    enrich()
    # validate_and_analyse()