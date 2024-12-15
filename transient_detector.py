import librosa
import os
import numpy as np
from scipy.signal import find_peaks

from piano_note_identifier import PianoNoteIdentifier
from audio_manager import AudioManager

class TransientDetector:
    def __init__(self, hop_length=512, verbose=False):
        self.hop_length = hop_length
        self.verbose = verbose

    def detect_transients(self, audio, sr, threshold=0.05, min_distance=1.0):
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)

        peaks, _ = find_peaks(
            onset_env,
            height=threshold * np.max(onset_env),
            distance=int(min_distance * sr / self.hop_length)
        )

        return librosa.frames_to_time(peaks, sr=sr, hop_length=self.hop_length)

    def process_transients(self, audio, sr, transients, output_dir, normalizer):
        note_identifier = PianoNoteIdentifier()
        for i, start_time in enumerate(transients):

            end_time = transients[i + 1] if i + 1 < len(transients) else len(audio) / sr
            clip_path = os.path.join(output_dir, f"note_{i + 1}.wav")

            AudioManager.save_audio_clip(audio, sr, start_time, end_time, clip_path)

            note_name = note_identifier.identify_note_and_name(audio[int(start_time * sr):int(end_time * sr)], sr)

            if note_name != "hammer":
                renamed_path = os.path.join(output_dir, f"{note_name}_note_{i + 1}.wav")
                os.rename(clip_path, renamed_path)
                clip_path = renamed_path

            normalizer.normalize_in_background(clip_path, os.path.join(output_dir, f"normalized_{os.path.basename(clip_path)}"))
