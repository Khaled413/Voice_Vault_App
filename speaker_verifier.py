from sklearn.mixture import GaussianMixture
import numpy as np
import joblib
import os

class SpeakerVerifier:
    def __init__(self, n_components=16, threshold=-50):
        self.n_components = n_components
        self.threshold = threshold
        self.models = {}
        self.models_dir = "models"
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def train_model(self, user_id, features):
        """Train a GMM model for a specific user."""
        gmm = GaussianMixture(
            n_components=self.n_components,
            covariance_type='diag',
            max_iter=200,
            random_state=42
        )
        
        gmm.fit(features)
        self.models[user_id] = gmm
        
        # Save the model
        model_path = os.path.join(self.models_dir, f"{user_id}_model.joblib")
        joblib.dump(gmm, model_path)
        
        return gmm
    
    def load_model(self, user_id):
        """Load a trained GMM model for a specific user."""
        model_path = os.path.join(self.models_dir, f"{user_id}_model.joblib")
        if os.path.exists(model_path):
            self.models[user_id] = joblib.load(model_path)
            return self.models[user_id]
        return None
    
    def verify_speaker(self, user_id, features):
        """Verify if the speaker matches the claimed identity."""
        if user_id not in self.models:
            # Try to load the model if it exists
            model = self.load_model(user_id)
            if model is None:
                return False, -float('inf')
        
        # Calculate log-likelihood
        log_likelihood = self.models[user_id].score(features)
        
        # Make decision based on threshold
        is_verified = log_likelihood > self.threshold
        
        return is_verified, log_likelihood
    
    def delete_model(self, user_id):
        """Delete a user's voice model."""
        if user_id in self.models:
            del self.models[user_id]
        
        model_path = os.path.join(self.models_dir, f"{user_id}_model.joblib")
        if os.path.exists(model_path):
            os.remove(model_path)
    
    def list_users(self):
        """List all enrolled users."""
        return list(self.models.keys()) 