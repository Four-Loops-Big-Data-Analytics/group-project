from stage1_files import transcribe_from_files
from stage1_live import record_and_transcribe
from stage1_files_parallel import transcribe_dir_parallel
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
        option = input("\nChoose an option (1 for recordings, or 2 for live): ").strip()

        if option == "1":
            # Inner loop prompts for the parallel/serial choice
            while True:
                processing = input("If you want parallel processing enter p, else for serial enter s: ").strip().lower()
                
                if processing == "p":
                    num_cores = input("How many cores would you like to use? Enter a number from 1 to 15. Hit enter for default value: ").strip()
                    
                    if not num_cores:
                        transcribe_dir_parallel(RECORDINGS_DIR)
                        break
                    
                    try:
                        num_cores = int(num_cores)
                        if 1 <= num_cores <= 15:
                            transcribe_dir_parallel(RECORDINGS_DIR, num_cores)
                            break 
                        else:
                            print(f"{num_cores} is not a valid number of cores. Please choose from 1 to 15.")
                    
                    except ValueError:
                        print(f"Cannot read an integer from '{num_cores}', please try again.")
                        continue
                
                elif processing == "s":
                    transcribe_from_files(RECORDINGS_DIR)
                    break
                
                else:
                    print("Invalid choice. Please enter 'p' or 's'.")
            
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

    analyse_csv("meeting_validated.csv")