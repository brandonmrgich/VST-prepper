#!/usr/bin/env python3

import os
import sys
import logging

from normalize_audio import AudioNormalizer
from transient_detector import TransientDetector
from audio_processor import AudioProcessor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

VERBOSE=True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Usage: python script.py <input_audio_files> <output_directory>")
        sys.exit(1)

    logging.info("Starting...")

    input_files = sys.argv[1:-1]
    output_directory = sys.argv[-1]
    os.makedirs(output_directory, exist_ok=True)

    normalizer = AudioNormalizer(max_workers=4, verbose=VERBOSE)

    logging.info("Normalizer init")

    # Overriding 512 hop_length for 256. Higher precision, less efficient
    #transient_detector = TransientDetector(hop_length=256, verbose=VERBOSE)

    transient_detector = TransientDetector(hop_length=512, verbose=VERBOSE)

    logging.info("TransientDetector init")

    processor = AudioProcessor(normalizer, transient_detector, verbose=VERBOSE)

    logging.info("AudioProcessor init")

    processor.process_audio_files(input_files, output_directory)

