import librosa
import logging
import os
import numpy as np
from scipy.signal import find_peaks

from piano_note_identifier import PianoNoteIdentifier
from audio_manager import AudioManager


class TransientDetector:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def detect_transients(
        self, audio, sr, threshold=0.05, min_distance=1.0, hop_length=512
    ):
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)

        peaks, _ = find_peaks(
            onset_env,
            height=threshold * np.max(onset_env),
            distance=int(min_distance * sr / hop_length),
        )

        return librosa.frames_to_time(peaks, sr=sr, hop_length=hop_length)

    # TODO: more aggressive offset
    def process_transients(
        self, audio, sr, transients, output_dir, normalizer, frame_offset=0.090
    ):
        """
        param: frame_offset: Adjust the start_time of the frame by subtracting <frame_offset>,
                or 90ms (0.090 seconds) for better inclusion of the initial impact

        """

        note_identifier = PianoNoteIdentifier()
        for i, start_time in enumerate(transients):
            #
            # Ensure no negative start times
            # TODO: 0 1 3 0 start delay for some transient detection
            adjusted_start_time = max(0, max(start_time - frame_offset, start_time))

            end_time = transients[i + 1] if i + 1 < len(transients) else len(audio) / sr

            clip_path = os.path.join(output_dir, f"note_{i + 1}.wav")
            logging.debug("TransientDetector::process_transients():", clip_path)

            AudioManager.save_audio_clip(audio, sr, start_time, end_time, clip_path)

            note_name = note_identifier.identify_note_and_name(
                audio[int(adjusted_start_time * sr) : int(end_time * sr)], sr
            )

            if note_name != "hammer":
                renamed_path = os.path.join(output_dir, f"{note_name}_note_{i + 1}.wav")
                os.rename(clip_path, renamed_path)
                clip_path = renamed_path

            normalizer.normalize_in_background(
                clip_path,
                os.path.join(output_dir, f"normalized_{os.path.basename(clip_path)}"),
            )
