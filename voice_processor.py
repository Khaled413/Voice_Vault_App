import librosa
import numpy as np
import os
from sklearn.preprocessing import StandardScaler

class VoiceProcessor:
    def __init__(self, n_mfcc=13, n_fft=2048, hop_length=512):
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.scaler = StandardScaler()
        
    def extract_features(self, audio_path):
        """Extract MFCC features from an audio file."""
        # Load audio file
        y, sr = librosa.load(audio_path, sr=None)
        
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(
            y=y,
            sr=sr,
            n_mfcc=self.n_mfcc,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        
        # Calculate delta and delta-delta features
        delta_mfccs = librosa.feature.delta(mfccs)
        delta2_mfccs = librosa.feature.delta(mfccs, order=2)
        
        # Stack all features
        features = np.vstack([mfccs, delta_mfccs, delta2_mfccs])
        
        return features.T  # Transpose to get (n_frames, n_features)
    
    def process_enrollment_samples(self, audio_files):
        """Process multiple enrollment samples and return combined features."""
        all_features = []
        
        for audio_file in audio_files:
            features = self.extract_features(audio_file)
            all_features.append(features)
            
        # Stack all features
        combined_features = np.vstack(all_features)
        
        # Fit scaler and transform features
        self.scaler.fit(combined_features)
        scaled_features = self.scaler.transform(combined_features)
        
        return scaled_features
    
    def process_verification_sample(self, audio_file):
        """Process a single verification sample."""
        features = self.extract_features(audio_file)
        scaled_features = self.scaler.transform(features)
        return scaled_features 