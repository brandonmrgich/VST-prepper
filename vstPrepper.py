#!/usr/bin/env python3

import os
import sys

from normalize_audio import AudioNormalizer

MSGPRE="vstPrepper"

futures = [] # List to track background tasks

# Default 512: Lower values increase precision, but increases runtime

VERBOSE=False

def create_output_directory(base_dir, note_name):
    """Create directory for the note if it doesn't exist."""
    note_dir = os.path.join(base_dir, note_name)
    os.makedirs(note_dir, exist_ok=True)
    return note_dir



def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python vstPrepper.py <input_audio_files> <output_directory>")
        sys.exit(1)

    input_files = sys.argv[1:-1]
    output_base_dir = sys.argv[-1]

    # Ensure output directory exists
    os.makedirs(output_base_dir, exist_ok=True)

    # Initialize the normalizer with a max of 4 concurrent threads
    normalizer = AudioNormalizer(max_workers=4, VERBOSE)

    # Process the input audio files
    process_audio_files(input_files, output_base_dir, normalizer)

if __name__ == "__main__":
    main()

