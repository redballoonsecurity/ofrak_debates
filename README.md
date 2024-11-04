# ofrak debates

Process debate archives and generate AI voices locally for responses using [F5-TTS](https://github.com/SWivid/F5-TTS). It extracts question-answer pairs from a zip archive and creates corresponding audio files for each response.

## Installation
1. Clone the repo:

```bash
git clone https://github.com/redballoonsecurity/ofrak_debates.git 
cd ofrak_debates
```

2. Create and activate a virtual environment (assuming Linux):

```bash
python -m venv .venv
source .venv/bin/activate  
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Start the [F5-TTS](https://github.com/SWivid/F5-TTS) Gradio server:

```bash
f5-tts_infer-gradio --port 7860 --host 0.0.0.0 # first time run will download the model files.
```

## Usage

The script processes a zip archive containing debate questions and responses, generating AI voice audio files for each response.

```bash
python record_debate.py --debate-archive path/to/your/debate.zip
```

### Expected Archive Structure

The input zip archive should have the following structure:
```
debate.zip
├── question1/
│   ├── question
│   ├── trump_answer
│   └── harris_answer
├── question2/
│   ├── question
│   ├── trump_answer
│   └── harris_answer
...
```

### Output

The script generates WAV files for each response:
- `Questions/Question-i/Trump.wav` - Trump's response for question i
- `Questions/Question-i/Harris.wav` - Harris's response for question i

## Configuration

You can modify the following parameters in the `gradio_get_ai_voice` function:
- `remove_silence`: Remove silence between generated batches
- `cross_fade_duration`: Fade-in duration between batches
- `speed`: Playback speed of the output

## Notes

- The Gradio server must be running on `http://0.0.0.0:7860` before executing the script
- Reference voice files should be in MP3 or WAV format
- Reference voice files should be below 15 seconds for best results.