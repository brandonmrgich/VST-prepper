import librosa
import os
import numpy as np


class TransientDetector:
    HOP_LENGTH=256

    def __init__(self, VERBOSE=False):
        self.VERBOSE=VERBOSE

    def detect_transients(audio, sr, threshold=0.05, min_distance=1.0):
        """Detect transients in the audio signal."""
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        peaks, _ = find_peaks(
            onset_env,
            height=threshold * np.max(onset_env),
            distance=int(min_distance * sr / (HOP_LENGTH))
        )
        return librosa.frames_to_time(peaks, sr=sr)
    
    def process_transients(audio, sr, transients, output_dir, normalizer):
        """Process the detected transients into clips and trigger normalization."""
        note_identifier = PianoNoteIdentifier()  # Create an instance of the note identifier
        note_number = 1
    
        for i, start_time in enumerate(transients):
            end_time = transients[i + 1] if i + 1 < len(transients) else len(audio) / sr
            note_clip_path = os.path.join(output_dir, f"note_{note_number}.wav")
            
            # Save the audio clip for the note
            save_audio_clip(audio, sr, start_time, end_time, note_clip_path)
    
            # Identify the note and rename the file accordingly
            note_name = note_identifier.identify_note_and_name(audio[int(start_time * sr):int(end_time * sr)], sr)
            if note_name != "hammer":
                # Rename the file with the note name
                note_clip_path_renamed = os.path.join(output_dir, f"{note_name}_note_{note_number}.wav")
                os.rename(note_clip_path, note_clip_path_renamed)
                note_clip_path = note_clip_path_renamed  # Update the path with the renamed one
    
            # Normalize the audio in the background
            normalizer.normalize_in_background(note_clip_path, os.path.join(output_dir, f"normalized_{note_name}_note_{note_number}.wav"))
    
            # Hammer clip logic
            hammer_start_time = end_time
            hammer_end_time = min(hammer_start_time + 2.0, len(audio) / sr)
            hammer_transients = detect_transients(audio[int(hammer_start_time * sr):int(hammer_end_time * sr)], sr)
    
            if hammer_transients.any():
                hammer_clip_path = os.path.join(output_dir, f"note_{note_number}_hammer.wav")
                save_audio_clip(audio, sr, hammer_start_time, hammer_end_time, hammer_clip_path)
                normalizer.normalize_in_background(hammer_clip_path, os.path.join(output_dir, f"normalized_hammer_{note_number}.wav"))
            
            note_number += 1
