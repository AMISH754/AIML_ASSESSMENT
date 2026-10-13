# Voice Signal Analysis: EC24313 AI & ML Assessment 1

**Department of Electronics and Communication Engineering, BIT Mesra, Ranchi**
**Author:** Amish Kumar Dubey (BTECH/10289/24)

This program records your voice saying **"BIT"** followed by **your name** in a single recording, then automatically:

1. Saves the recording as `YOURNAME_BIT_Name.wav`
2. Plots the time-domain waveform and finds the sampling frequency
3. Detects and marks the silent (unvoiced) regions, including the pause between the two words
4. Removes the silent regions and saves the trimmed audio
5. Plots the spectrogram using the Short-Time Fourier Transform (STFT)

## Requirements

- [Python](https://www.python.org/downloads/) 3.10 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- A working microphone

## Setup (one time)

Open a terminal in the project folder and run:

```bash
uv venv
```

```bash
uv pip install numpy scipy matplotlib sounddevice soundfile
```

The first command creates a virtual environment in a `.venv` folder, and the second installs the required libraries into it.

## Run

**Windows:**

```bash
.venv/Scripts/python.exe aiml_assessment.py
```

**macOS / Linux:**

```bash
.venv/bin/python aiml_assessment.py
```

To use the **▶ Run** button in VS Code instead, press `Ctrl + Shift + P`, choose **Python: Select Interpreter**, and select the `.venv` interpreter.

## How to use

1. Enter your name when asked (e.g. `Rohit`). Spaces and symbols are converted to underscores automatically.
2. Press **Enter** and wait for the countdown.
3. When you see `>>> SPEAK NOW <<<`, say **"BIT"**, pause for about 1 second, then say **your name**. The recording lasts 5 seconds.
4. Type `y` to record again, or press **Enter** to keep the recording.
5. The plots then appear on screen and are saved automatically.

**Tip:** Stay silent for a moment after "SPEAK NOW" and after your name, so the program has clear silent regions to detect.

## Output

```
AIML Assesment/
├── YOURNAME_BIT_Name.wav                       # Original recording ("BIT" + name)
└── outputs/
    ├── YOURNAME_BIT_Name_Q2_waveform.png        # Time-domain waveform
    ├── YOURNAME_BIT_Name_Q3_silence_marked.png  # Silent regions marked in red
    ├── YOURNAME_BIT_Name_Q4_trimmed.png         # Before vs. after silence removal
    ├── YOURNAME_BIT_Name_Q5_spectrogram.png     # Spectrogram
    └── YOURNAME_BIT_Name_trimmed.wav            # Audio with silence removed
```

The terminal also prints the sampling frequency, signal duration before and after trimming, and the exact time ranges of the silent and voiced regions.

## Settings

These values at the top of `aiml_assessment.py` can be adjusted:

| Setting    | Default | Purpose                                                      |
|------------|---------|--------------------------------------------------------------|
| `FS`       | 44100   | Recording sampling frequency (Hz)                            |
| `DURATION` | 5       | Length of the recording (seconds)                            |
| `TOP_DB`   | 30      | Silence threshold in dB below the loudest part of the signal |

## Troubleshooting

**No sound recorded / "very quiet" warning:** On Windows, go to *Settings → Privacy & security → Microphone* and allow desktop apps to use the microphone. On macOS, allow your terminal or VS Code under *System Settings → Privacy & Security → Microphone*.

**Parts of the words are cut off after trimming:** Increase `TOP_DB` to `40`.

**Background noise is treated as speech:** Decrease `TOP_DB` to `20`.

**The pause between "BIT" and the name is not marked as silence:** Pause a little longer (about 1 second) between the two words.

**Not enough time to say both words:** Increase `DURATION` to `6` or `7`.

**`ModuleNotFoundError: No module named 'numpy'`:** You are running a different Python. Use the `.venv` command shown in the Run section.

**`externally-managed-environment` error:** Don't install with `pip` directly into uv's Python. Follow the Setup steps above to create a `.venv` instead.

**`uv: command not found`:** Install uv using the link in Requirements, then restart the terminal.
