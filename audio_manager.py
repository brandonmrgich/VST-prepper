import logging
import librosa
import soundfile as sf

class AudioManager:

    @staticmethod
    def load_audio(audio_path):
        try:
            return librosa.load(audio_path, sr=None)
        except Exception as e:
            logging.error(f"Error loading {audio_path}: {e}")
            return None, None

    @staticmethod
    def save_audio_clip(audio, sr, start_time, end_time, output_path):
        start_sample = int(start_time * sr)
        end_sample = int(min(end_time * sr, len(audio)))
        if start_sample < end_sample:
            sf.write(output_path, audio[start_sample:end_sample], sr)
