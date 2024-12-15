

import librosa
import numpy as np

class PianoNoteIdentifier:
    # Frequencies for the 88 notes on a standard piano
    STANDARD_A4 = 440.0  # Frequency of A4 (440 Hz)
    CENTS_FLAT = 60  # 60 cents flat tuning
    
    # MIDI note numbers for the 88 keys on a standard piano (A0 to C8)
    MIDI_NOTES = {
        21: "A0", 22: "A#0", 23: "B0", 24: "C1", 25: "C#1", 26: "D1", 27: "D#1", 28: "E1", 29: "F1", 30: "F#1", 31: "G1", 32: "G#1",
        33: "A1", 34: "A#1", 35: "B1", 36: "C2", 37: "C#2", 38: "D2", 39: "D#2", 40: "E2", 41: "F2", 42: "F#2", 43: "G2", 44: "G#2",
        45: "A2", 46: "A#2", 47: "B2", 48: "C3", 49: "C#3", 50: "D3", 51: "D#3", 52: "E3", 53: "F3", 54: "F#3", 55: "G3", 56: "G#3",
        57: "A3", 58: "A#3", 59: "B3", 60: "C4", 61: "C#4", 62: "D4", 63: "D#4", 64: "E4", 65: "F4", 66: "F#4", 67: "G4", 68: "G#4",
        69: "A4", 70: "A#4", 71: "B4", 72: "C5", 73: "C#5", 74: "D5", 75: "D#5", 76: "E5", 77: "F5", 78: "F#5", 79: "G5", 80: "G#5",
        81: "A5", 82: "A#5", 83: "B5", 84: "C6", 85: "C#6", 86: "D6", 87: "D#6", 88: "E6", 89: "F6", 90: "F#6", 91: "G6", 92: "G#6",
        93: "A6", 94: "A#6", 95: "B6", 96: "C7", 97: "C#7", 98: "D7", 99: "D#7", 100: "E7", 101: "F7", 102: "F#7", 103: "G7", 104: "G#7",
        105: "A7", 106: "A#7", 107: "B7", 108: "C8"
    }

    @staticmethod
    def frequency_to_midi_note(frequency):
        """Convert frequency to MIDI note number."""
        return 69 + 12 * np.log2(frequency / PianoNoteIdentifier.STANDARD_A4)

    @staticmethod
    def get_note_name(frequency):
        """Get the note name based on frequency, adjusted for 60 cents flat."""
        # Adjust the frequency for the 60-cent flat tuning
        adjusted_frequency = frequency * 2 ** (-PianoNoteIdentifier.CENTS_FLAT / 1200)
        midi_note = round(PianoNoteIdentifier.frequency_to_midi_note(adjusted_frequency))
        
        # If the MIDI note is within the 88-note piano range, get its name
        if 21 <= midi_note <= 108:
            return PianoNoteIdentifier.MIDI_NOTES[midi_note]
        return None  # No note identified, probably a hammer sound

    @staticmethod
    def detect_pitch(audio, sr):
        """Detect the pitch (fundamental frequency) of the audio."""
        # Use librosa to compute the onset strength envelope
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        onset_env = librosa.util.normalize(onset_env)
        pitches, magnitudes = librosa.core.piptrack(y=audio, sr=sr)
        
        # Ensure that magnitudes array has valid data
        if magnitudes.size > 0:
            # Find the index of the maximum magnitude within bounds
            max_index = np.unravel_index(np.argmax(magnitudes), magnitudes.shape)
            # Extract the corresponding pitch (fundamental frequency) using the max index
            pitch = pitches[max_index]

            # Check if pitch is a valid number (greater than 0)
            if pitch > 0:
                return pitch
        return None  # If no valid pitch is detected

    def identify_note_and_name(self, audio, sr):
        """Identify the note for the given audio segment."""
        pitch = self.detect_pitch(audio, sr)
        if pitch is not None:
            note_name = self.get_note_name(pitch)
            if note_name:
                return note_name
        return "hammer"  # If no pitch is detected or no note found

