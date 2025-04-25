import sounddevice as sd
import numpy as np
import wave
import os
from datetime import datetime

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1, duration=3):
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration
        self.recording = None
        
    def record_audio(self):
        """Record audio for a specified duration."""
        print(f"Recording for {self.duration} seconds...")
        self.recording = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32'
        )
        sd.wait()
        print("Recording complete!")
        return self.recording
    
    def save_recording(self, filename, directory="recordings"):
        """Save the recorded audio to a WAV file."""
        if self.recording is None:
            raise ValueError("No recording available to save")
            
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        # Ensure filename has .wav extension
        if not filename.endswith('.wav'):
            filename += '.wav'
            
        filepath = os.path.join(directory, filename)
        
        # Convert float32 to int16
        audio_data = (self.recording * 32767).astype(np.int16)
        
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
            
        print(f"Recording saved to {filepath}")
        return filepath
    
    def play_recording(self):
        """Play back the recorded audio."""
        if self.recording is None:
            raise ValueError("No recording available to play")
            
        print("Playing recording...")
        sd.play(self.recording, self.sample_rate)
        sd.wait()
        print("Playback complete!") 