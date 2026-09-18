# %% [markdown]
# # 21 - Whisper Speech-to-Text (multilingual)
#
# Convert audio files to text locally, fully offline.
# Uses the `openai-whisper` package with the `small` model.
#
# Supported formats: .wav, .mp3, .flac, .ogg, .m4a

# %%
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

from toolkit.transcribe import (
    transcribe_to_text,
    transcribe_segments,
    transcribe_to_srt,
)

print("Whisper helpers loaded.")

# %% [markdown]
# ## 1. Load the model
#
# The first call downloads the `small` model (~466 MB).
# After that it is cached and works offline.

# %%
# Point this to your own audio file
AUDIO_FILE = Path("data/audio/sample.wav")

# If you don't have a file, this cell creates a tiny silent wav for testing.
if not AUDIO_FILE.exists():
    AUDIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    import wave, struct
    with wave.open(str(AUDIO_FILE), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        for _ in range(16000):  # 1 second of silence
            w.writeframes(struct.pack("<h", 0))
    print(f"Created test file: {AUDIO_FILE}")
else:
    print(f"Using existing file: {AUDIO_FILE}")

# %% [markdown]
# ## 2. Transcribe to plain text

# %%
text = transcribe_to_text(AUDIO_FILE, model="small", language=None)
print("--- Transcribed text ---")
print(text)

# %% [markdown]
# ## 3. Transcribe with timestamps

# %%
segments = transcribe_segments(AUDIO_FILE, model="small", language=None)
print(f"{len(segments)} segments\n")
for seg in segments:
    print(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")

# %% [markdown]
# ## 4. Save as SRT subtitle file

# %%
srt_path = Path("exports/transcript.srt")
transcribe_to_srt(AUDIO_FILE, srt_path, model="small", language=None)
print(f"Saved: {srt_path}")

# %%
# Show the first few lines
if srt_path.exists():
    print()
    print("--- SRT preview ---")
    print("\n".join(srt_path.read_text(encoding="utf-8").splitlines()[:12]))

# %% [markdown]
# ## 5. Try different models
#
# | Model  | Size   | Speed on CPU | Quality (multilingual) |
# |--------|--------|--------------|-------------------|
# | tiny   | 75 MB  | fastest      | low               |
# | base   | 142 MB | fast         | ok                |
# | small  | 466 MB | medium       | good (default)    |
# | medium | 1.5 GB | slow         | very good         |
#
# Change the `model` argument to try others.

# %%
# Uncomment to try a faster model:
# text = transcribe_to_text(AUDIO_FILE, model="base", language=None)
# print(text)