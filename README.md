## Big Data Analytics Group Project
### Birkbeck University 2026
### Team: Four Loops
Four Loops are:  
Dan Papier  
Marcos  
Aidan  
Edward Emmett  

### Set-up  
Download ```vosk-model-en-us-0.22-lgraph``` from https://alphacephei.com/vosk/models.  
Make sure it is placed inside the project root directory ```group-project/```.

Add your recordings in format ```.wav```, with a sample rate of 16kHz, to ```group-project/recordings```. This is the specific file format required by the Vosk transcription model.

### Complexity discussion
We have made an effort to save output (transcriptions, AI corrections, analytics, etc) to RAM (ie data structures such as lists) before writing to file.
An improved solution could assign multiple threads to calling the Vosk transcription model in parallel.
A significant bottleneck is calling the Gemini API, which has strict request limits per API key.
In stage4.py for example, we attempted to reduce memory usage by streaming the .csv input file line by line and performing all validation checks at once. That is, we only loop through the file once. Log entries and errors are saved to RAM
