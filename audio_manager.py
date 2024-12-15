import librosa

class AudioManager:
    def __init__(self, VERBOSE=False):
        self.VERBOSE=VERBOSE

    def load_audio(audio_path):
        """Load audio from the given path using librosa."""
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            return audio, sr
        except Exception as e:
            print(f"Error loading {audio_path}: {e}")
            return None, None
    
    
    def save_audio_clip(audio, sr, start_time, end_time, output_path):
        """Save a segment of audio to a file."""
        start_sample = int(start_time * sr)
        end_sample = int(min(end_time * sr, len(audio)))  # Ensure within bounds
        if start_sample < end_sample:  # Only save if the segment is valid
            sf.write(output_path, audio[start_sample:end_sample], sr)
    
    
    def process_audio_file(audio_path, output_dir, normalizer):
        """Process an audio file, detecting transients and triggering normalization."""
        audio, sr = load_audio(audio_path)
        if audio is None:
            return  # Skip the file if loading failed
        
        transients = detect_transients(audio, sr)
        process_transients(audio, sr, transients, output_dir, normalizer)
    
    def process_audio_files(input_files, output_base_dir, normalizer):
        """Process all input audio files."""
        for input_audio in input_files:
    
            if VERBOSE:
                print(f"Processing {input_audio}...")
    
            output_dir = create_output_directory(output_base_dir, os.path.splitext(os.path.basename(input_audio))[0])
            process_audio_file(input_audio, output_dir, normalizer)
