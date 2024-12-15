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

        # Extract the file name without extension to create the output directory
        # audio_file_1.wav -> audio_file_1/
        file_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_file_dir = os.path.join(output_dir, file_name)
        os.makedirs(output_file_dir, exist_ok=True)

        logging.info("AudioProcessor::process_audio_file(): Detecting transients")
        transients = self.transient_detector.detect_transients(audio, sr)

        # Save the clips in the created directory
        logging.info("AudioProcessor::process_audio_file(): Processing transients")
        self.transient_detector.process_transients(audio, sr, transients, output_file_dir, self.normalizer)

    def process_audio_files(self, input_files, output_dir):
        for audio_file in input_files:

            if self.verbose:
                logging.debug(f"Processing {audio_file}...")

            self.process_audio_file(audio_file, output_dir)
