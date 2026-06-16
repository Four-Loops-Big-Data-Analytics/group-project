from stage2_gemini import record_corrected_lines_gemini
from stage2_ollama import record_corrected_lines_ollama_parallel, record_corrected_lines_ollama_serial

if __name__ == "__main__":

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
                print("Invalid choice. Please enter 1 or 2.")
                break
        else:
            print("Invalid choice. Please enter gemini or ollama.")