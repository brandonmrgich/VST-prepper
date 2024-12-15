from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
import logging
import os

class AudioNormalizer:
    def __init__(self, max_workers=None, verbose=False):
        """Initialize the AudioNormalizer with an optional number of threads."""
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.verbose = verbose

    def normalize_audio(self, input_path, output_path):
        """Normalize audio to -1 dBFS and handle cleanup."""
        try:
            audio = AudioSegment.from_file(input_path)
            normalized_audio = audio.apply_gain(-audio.max_dBFS - 1)  # Normalize without clipping
            normalized_audio.export(output_path, format="wav")

            if self.verbose:
                logging.info(f"Normalized and saved: {output_path}")

            # Perform cleanup: Remove the original file after processing
            os.remove(input_path)
            if self.verbose:
                logging.info(f"Removed original file: {input_path}")
        except Exception as e:
            logging.error(f"Error processing {input_path}: {e}")

    def normalize_in_background(self, input_path, output_path):
        """Run the normalization in a non-blocking way."""
        self.executor.submit(self.normalize_audio, input_path, output_path)
