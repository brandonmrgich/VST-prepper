import logging
import os

from audio_manager import AudioManager

class AudioProcessor:
    def __init__(self, normalizer, transient_detector, verbose=False):
        self.normalizer = normalizer
        self.transient_detector = transient_detector
        self.verbose = verbose

    def process_audio_file(self, audio_path, output_dir):
        audio, sr = AudioManager.load_audio(audio_path)
        if audio is None:
            return

        logging.info("AudioProcessor::process_audio_file(): Detecting transients")
        transients = self.transient_detector.detect_transients(audio, sr)

        logging.info("AudioProcessor::process_audio_file(): Processing transients")
        self.transient_detector.process_transients(audio, sr, transients, output_dir, self.normalizer)

    def process_audio_files(self, input_files, output_dir):
        for audio_file in input_files:
            if self.verbose:
                logging.info(f"Processing {audio_file}...")

            # Get the relative path of the audio file
            relative_path = os.path.relpath(audio_file, start=os.path.commonpath(input_files))

            # Create the full output path by joining the output directory with the relative path
            output_path = os.path.join(output_dir, relative_path)

            # Create the directory structure if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Process the individual audio file
            self.process_audio_file(audio_file, os.path.dirname(output_path))
