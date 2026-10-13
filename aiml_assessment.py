"""
EC24313 AI & ML - Assessment 1
Records "BIT" and "Your Name", then:
 Q2: plots the waveform and reports the sampling frequency
 Q3: marks the silent / unvoiced regions
 Q4: removes the silence and saves the trimmed audio
 Q5: plots the spectrogram (STFT)
"""

import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import stft

# ------------------ Settings ------------------
FS = 44100          # sampling frequency for recording (Hz)
DURATION = 3        # seconds per recording
TOP_DB = 30         # frames this many dB below the loudest frame count as silence
FRAME_MS = 25       # analysis frame length (ms)
HOP_MS = 10         # frame step (ms)
OUT_DIR = "outputs"
# ----------------------------------------------


def record_word(filename, prompt):
    """Q1: Record audio from the microphone and save it as a .wav file."""
    while True:
        input(f"\nPress ENTER, then say {prompt}  ({DURATION} s recording)")
        for i in (3, 2, 1):
            print(f"  Starting in {i}...")
            time.sleep(1)
        print("  >>> SPEAK NOW <<<")
        audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype="float32")
        sd.wait()
        audio = audio.flatten()
        print("  Recording finished.")

        if np.max(np.abs(audio)) < 0.01:
            print("  WARNING: Very quiet recording. Check your microphone.")

        again = input("  Re-record this one? (y/N): ").strip().lower()
        if again != "y":
            sf.write(filename, audio, FS)
            print(f"  Saved as {filename}")
            return filename


def find_voiced_intervals(y, sr):
    """Q3: Energy-based voice activity detection. Returns [(start, end), ...] in samples."""
    frame = int(FRAME_MS * sr / 1000)
    hop = int(HOP_MS * sr / 1000)
    n_frames = 1 + max(0, (len(y) - frame) // hop)

    rms = np.array([np.sqrt(np.mean(y[i*hop : i*hop + frame] ** 2)) for i in range(n_frames)])
    db = 20 * np.log10(rms / (rms.max() + 1e-12) + 1e-12)
    active = db > -TOP_DB

    # Convert active frames into sample intervals
    intervals, start = [], None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            intervals.append((start * hop, (i - 1) * hop + frame))
            start = None
    if start is not None:
        intervals.append((start * hop, len(y)))

    # Merge gaps shorter than 100 ms (e.g. inside a word) and drop blips under 50 ms
    merged = []
    for s, e in intervals:
        if merged and s - merged[-1][1] < 0.10 * sr:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    merged = [(s, min(e, len(y))) for s, e in merged if e - s >= 0.05 * sr]
    return merged


def silent_intervals(voiced, n):
    """Complement of the voiced intervals."""
    silent, prev = [], 0
    for s, e in voiced:
        if s > prev:
            silent.append((prev, s))
        prev = e
    if prev < n:
        silent.append((prev, n))
    return silent


def analyse(path):
    name = os.path.splitext(os.path.basename(path))[0]
    y, sr = sf.read(path)
    if y.ndim > 1:
        y = y.mean(axis=1)
    t = np.arange(len(y)) / sr

    print(f"\n========== {name} ==========")
    print(f"Sampling frequency fs = {sr} Hz")
    print(f"Duration = {len(y)/sr:.2f} s, Number of samples = {len(y)}")

    # ---------- Q2: Time-domain waveform ----------
    plt.figure(figsize=(12, 3.5))
    plt.plot(t, y, lw=0.6)
    plt.title(f"Q2: Time-domain waveform of '{name}'  (fs = {sr} Hz)")
    plt.xlabel("Time (s)"); plt.ylabel("Amplitude"); plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/{name}_Q2_waveform.png", dpi=150)

    # ---------- Q3: Mark silent regions ----------
    voiced = find_voiced_intervals(y, sr)
    if not voiced:
        print("No speech detected; try lowering TOP_DB or recording louder.")
        voiced = [(0, len(y))]
    silent = silent_intervals(voiced, len(y))

    plt.figure(figsize=(12, 3.5))
    plt.plot(t, y, lw=0.6, color="tab:blue")
    for i, (s, e) in enumerate(silent):
        plt.axvspan(s/sr, e/sr, color="red", alpha=0.25,
                    label="Silence / unvoiced zone" if i == 0 else None)
    for i, (s, e) in enumerate(voiced):
        plt.axvspan(s/sr, e/sr, color="green", alpha=0.15,
                    label="Voiced region" if i == 0 else None)
    plt.title(f"Q3: Silent regions marked in '{name}'  (threshold = -{TOP_DB} dB)")
    plt.xlabel("Time (s)"); plt.ylabel("Amplitude"); plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/{name}_Q3_silence_marked.png", dpi=150)

    print("Silent regions (s):", [(round(s/sr, 2), round(e/sr, 2)) for s, e in silent])
    print("Voiced regions (s):", [(round(s/sr, 2), round(e/sr, 2)) for s, e in voiced])

    # ---------- Q4: Remove silence ----------
    y_trim = np.concatenate([y[s:e] for s, e in voiced])
    trimmed_path = f"{OUT_DIR}/{name}_trimmed.wav"
    sf.write(trimmed_path, y_trim, sr)
    print(f"Duration before = {len(y)/sr:.2f} s, after trimming = {len(y_trim)/sr:.2f} s")
    print(f"Trimmed audio saved as {trimmed_path}")

    fig, ax = plt.subplots(2, 1, figsize=(12, 6))
    ax[0].plot(t, y, lw=0.6)
    ax[0].set_title(f"Original signal ({len(y)/sr:.2f} s)")
    ax[1].plot(np.arange(len(y_trim)) / sr, y_trim, lw=0.6, color="tab:green")
    ax[1].set_title(f"Q4: After removing silence ({len(y_trim)/sr:.2f} s)")
    for a in ax:
        a.set_xlabel("Time (s)"); a.set_ylabel("Amplitude"); a.grid(alpha=0.3)
    plt.suptitle(name)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/{name}_Q4_trimmed.png", dpi=150)

    # ---------- Q5: Spectrogram (STFT) ----------
    nperseg, noverlap = 1024, 768
    f, tt, Z = stft(y_trim, fs=sr, window="hann", nperseg=nperseg, noverlap=noverlap)
    S_db = 20 * np.log10(np.abs(Z) + 1e-10)
    S_db -= S_db.max()

    plt.figure(figsize=(12, 4.5))
    plt.pcolormesh(tt, f, S_db, shading="gouraud", cmap="magma", vmin=-80, vmax=0)
    plt.colorbar(label="Magnitude (dB)")
    plt.ylim(0, min(8000, sr / 2))   # speech energy is mostly below 8 kHz
    plt.title(f"Q5: Spectrogram of trimmed '{name}'  (STFT, Hann window, N = {nperseg})")
    plt.xlabel("Time (s)"); plt.ylabel("Frequency (Hz)")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/{name}_Q5_spectrogram.png", dpi=150)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    name = input("Enter your name (e.g. Rohit): ").strip().replace(" ", "_") or "Student"
    print("Using microphone:", sd.query_devices(kind="input")["name"])
    print("Tip: stay quiet for a moment after 'SPEAK NOW' so there is silence to detect.")

    file_bit = record_word(f"{name}_BIT.wav", '"BIT"')
    file_name = record_word(f"{name}_Name.wav", f'your name "{name}"')

    analyse(file_bit)
    analyse(file_name)

    print(f"\nAll plots and trimmed audio saved in the '{OUT_DIR}' folder.")
    plt.show()