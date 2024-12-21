import librosa
import logging
import os
import numpy as np
from scipy.signal import find_peaks

from piano_note_identifier import PianoNoteIdentifier
from audio_manager import AudioManager


class TransientDetector:
    def __init__(
        self, verbose=False, lookahead_ms=150, energy_threshold=0.026, buffer_ms=50
    ):
        """
        Initialize the TransientDetector with the given parameters.

        Args:
            verbose (bool): If True, enables detailed logging for debugging and analysis.
            lookahead_ms (int): The size of the lookahead window (in milliseconds) used to predict when a transient ends.
            energy_threshold (float): The threshold for detecting the end of a transient based on energy. Lower values will detect quieter transients, while higher values will be more selective.
            buffer_ms (int): The buffer time (in milliseconds) to subtract from the start time of the next transient when calculating the end time of the current transient.

        Default parameter analysis:
        - **lookahead_ms (150 ms)**: A typical value for detecting transient end times. This provides a reasonable lookahead window to determine if energy has dropped off after a transient, allowing for smoother detection.
        - **energy_threshold (0.026)**: This value defines the sensitivity to energy drop-off. A higher value would require a more significant drop in energy before marking the end of a transient, while a lower value might falsely trigger an end too early.
        - **buffer_ms (50 ms)**: This buffer ensures that transients are not cut off prematurely. It's essential for ensuring a more natural and continuous transient detection.
        """

        self.verbose = verbose
        self.energy_threshold = energy_threshold
        self.lookahead_ms = lookahead_ms
        self.buffer_ms = buffer_ms

    def calculate_lookahead_samples(self, sr):
        """Calculate the number of samples corresponding to the lookahead window."""
        return int((self.lookahead_ms / 1000) * sr)

    def calculate_buffer_samples(self, sr):
        """Calculate the number of samples corresponding to the buffer window."""
        return int((self.buffer_ms / 1000) * sr)

    def detect_transients(
        self, audio, sr, threshold=0.05, min_distance=0.3, hop_length=720
    ):
        """
        Detects transients in the given audio by analyzing the onset strength.

        Args:
            audio (np.ndarray): The audio waveform data.
            sr (int): The sample rate of the audio.
            threshold (float): The minimum peak height relative to the maximum onset strength to consider a peak as a transient.
            min_distance (float): The minimum distance (in seconds) between consecutive transients to avoid detecting too many closely spaced peaks.
            hop_length (int): The number of samples between each frame for the onset strength calculation.

        Math explanation:
        - **Onset Strength Calculation**: The onset envelope is calculated using librosa's onset strength function, which measures the sudden increase in energy (e.g., the attack of a sound). The peaks of this onset envelope correspond to transients.
        - **Peak Detection**: The `find_peaks` function is used to find peaks in the onset envelope. The threshold parameter defines the minimum relative height of a peak, ensuring that only significant events are detected. The `min_distance` ensures that closely spaced transients are not detected as separate events.

        Recommended value ranges:
        - **threshold**: Values between 0.02 and 0.1 are typical. Lower values may lead to detecting more subtle events, while higher values might miss quieter transients.
        - **min_distance**: Typically between 0.2 and 0.5 seconds. A higher value will make the detector more selective in identifying transients that are spaced further apart, reducing false positives.
        """
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)

        peaks, _ = find_peaks(
            onset_env,
            height=threshold * np.max(onset_env),
            distance=int(min_distance * sr / hop_length),
        )

        return librosa.frames_to_time(peaks, sr=sr, hop_length=hop_length)

    # def calculate_end_time(self, audio_data, start_time, next_start_time, sr):
    #    """
    #    Calculate the end time of a transient based on energy decay and a lookahead window.

    #    Args:
    #        audio_data (np.ndarray): The audio waveform data.
    #        start_time (int): The start time (in samples) of the transient.
    #        next_start_time (int): The start time (in samples) of the next transient.
    #        sr (int): The sample rate of the audio.

    #    Returns:
    #        int: The calculated end time (in samples) of the current transient.

    #    Explanation:
    #    - **Energy Thresholding**: The transient end time is determined by monitoring the energy in the lookahead window. When the energy drops below the defined `energy_threshold`, the transient is considered to have ended.
    #    - **Lookahead Window**: The algorithm checks for a drop in energy over a window defined by `lookahead_samples`. If the energy stays below the threshold for the duration of this window, the transient is considered to have ended.

    #    Default behavior and recommended value ranges:
    #    - **lookahead_ms (150 ms)**: This lookahead window length is typically suitable for most transient detection scenarios. It balances between accurately detecting the end of transients and not introducing too much delay.
    #    - **energy_threshold (0.026)**: A higher threshold (e.g., 0.05) makes the algorithm more conservative, requiring a more significant energy drop to end a transient, while lower values (e.g., 0.01) may detect quieter transients as ending prematurely.
    #    """

    #    # Recalculated per file
    #    lookahead_samples = self.calculate_lookahead_samples(sr)
    #    buffer_samples = self.calculate_buffer_samples(sr)

    #    # lookahead_end = min(start_time + lookahead_samples, len(audio_data))
    #    lookahead_end = min(next_start_time, len(audio_data))

    #    msg = f"lookahead_end: {lookahead_end}"
    #    logging.debug(msg)

    #    ## If next transient is too close, adjust the lookahead window
    #    # if next_start_time - start_time < lookahead_samples:
    #    #    # If transients are too close, we don't want to skip over them, so we reduce the lookahead window
    #    #    lookahead_end = min(next_start_time, len(audio_data))

    #    # Analyze energy in the lookahead window
    #    for t in range(start_time, lookahead_end):
    #        window_energy = np.mean(audio_data[t : t + lookahead_samples] ** 2)
    #        msg = f"window_energy: {window_energy}, self.energy_threshold: {self.energy_threshold}"
    #        logging.info(msg)

    #        if window_energy < self.energy_threshold:
    #            msg = f"time: {t}, next_start_time: {next_start_time}"
    #            logging.info(msg)

    #            # Energy dropped below the threshold, return the time if it's before the next transient's start time
    #            if t < next_start_time:
    #                return t

    #    # Default: Use next transient's start time minus buffer minus .05 static to leave room
    #    # before the next transient
    #    return max(start_time, next_start_time - 0.05)

    def process_transients(
        self, audio, sr, transients, output_dir, normalizer, frame_offset=0.025
    ):
        """
        Process detected transients by calculating their end times, saving audio clips, and normalizing them.

        Args:
            audio (np.ndarray): The audio waveform data.
            sr (int): The sample rate of the audio.
            transients (list): A list of transient start times.
            output_dir (str): The directory to save the resulting audio clips.
            normalizer: An object that handles the normalization of audio clips.
            frame_offset (float): A time offset (in seconds) applied to the start time of the detected transients.

        Explanation:
        - **Note Detection**: After detecting a transient and calculating its end time, the clip is saved as a WAV file. The clip is then analyzed to identify the musical note being played using the `PianoNoteIdentifier`.
        - **Normalization**: Once the clip is saved and renamed based on the identified note, it is normalized using the provided normalizer object. This ensures that the clip's volume is consistent and within a desirable range.

        Effect of `frame_offset`:
        - **frame_offset (0.25)**: The `frame_offset` parameter adjusts the start time of each detected transient. A positive offset will shift the transient's start earlier, capturing more of the sound leading up to the peak. A larger value (e.g., 0.5) will give more room before the peak, potentially making the detection more inclusive of the initial attack phase.
        """
        if not transients.any():
            logging.warning("No transients detected.")
            return

        note_identifier = PianoNoteIdentifier()

        for i, start_time in enumerate(transients):
            msg = f"start_time: {start_time}"
            logging.debug(msg)

            # Safely get the next start time, if available
            next_start_time = (
                transients[i + 1] if i + 1 < len(transients) else len(audio) / sr
            )

            msg = f"next_start_time: {next_start_time}"
            logging.debug(msg)

            # Ensure no negative start times
            adjusted_start_time = max(0, start_time - frame_offset)
            next_start_time = max(adjusted_start_time, next_start_time - frame_offset)

            msg = f"adjusted_start_time: {adjusted_start_time}, next_start_time: {next_start_time}"
            logging.debug(msg)

            # Calculate end time using the lookahead approach
            # end_time = self.calculate_end_time(
            #    audio, adjusted_start_time, adjusted_start_time2, sr
            # )

            end_time = next_start_time

            msg = f"end_time: {end_time}"
            logging.debug(msg)

            # Define clip path and save the audio clip
            clip_path = os.path.join(output_dir, f"note_{i + 1}.wav")
            logging.info(
                f"TransientDetector::process_transients(): Saving clip at {clip_path}"
            )

            AudioManager.save_audio_clip(
                audio, sr, adjusted_start_time, end_time, clip_path
            )

            # Identify the note
            note_name = note_identifier.identify_note_and_name(
                audio[int(adjusted_start_time * sr) : int(end_time * sr)], sr
            )

            # Rename the clip based on the note name
            if note_name != "hammer":
                renamed_path = os.path.join(output_dir, f"{note_name}_note_{i + 1}.wav")
                os.rename(clip_path, renamed_path)
                clip_path = renamed_path

            # Normalize the clip in the background
            normalizer.normalize_in_background(
                clip_path,
                os.path.join(output_dir, f"normalized_{os.path.basename(clip_path)}"),
            )
