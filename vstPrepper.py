#!/usr/bin/env python3

import os
import sys
import logging
import argparse

from normalize_audio import AudioNormalizer
from transient_detector import TransientDetector
from audio_processor import AudioProcessor

# Set up argument parser
parser = argparse.ArgumentParser(
    description="Process audio files with transient detection and normalization."
)
parser.add_argument(
    "input_audio_files",
    nargs="+",
    help="List of input audio files or directories containing audio files.",
)
parser.add_argument(
    "output_directory", help="Directory to save the processed audio files."
)
parser.add_argument(
    "--log-level",
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Set the logging level (default: INFO)",
)

# Parse the command-line arguments
args = parser.parse_args()

# Set up logging based on the provided log level
logging.basicConfig(
    level=args.log_level.upper(), format="%(asctime)s - %(levelname)s - %(message)s"
)

VERBOSE = True

if __name__ == "__main__":
    if len(args.input_audio_files) < 1:
        logging.error("Usage: python script.py <input_audio_files> <output_directory>")
        sys.exit(1)

    logging.info("Starting...")

    input_files = args.input_audio_files
    output_directory = args.output_directory
    os.makedirs(output_directory, exist_ok=True)

    """Control threading with max_workers"""
    normalizer = AudioNormalizer(max_workers=4, verbose=VERBOSE)

    logging.debug("Normalizer init")

    # Overriding 512 hop_length for 256. Higher precision, less efficient
    # transient_detector = TransientDetector(hop_length=256, verbose=VERBOSE)

    transient_detector = TransientDetector(verbose=VERBOSE)

    logging.debug("TransientDetector init")

    processor = AudioProcessor(normalizer, transient_detector, verbose=VERBOSE)

    logging.debug("AudioProcessor init")

    processor.process_audio_files(input_files, output_directory)

    logging.info("Jobs complete, exiting.")

    exit(0)
    # TODO custom exceptions
    # TODO nice exit for 9 & 15
