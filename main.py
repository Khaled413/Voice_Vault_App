import os
import time
from audio_recorder import AudioRecorder
from voice_processor import VoiceProcessor
from speaker_verifier import SpeakerVerifier

class BankVaultSystem:
    def __init__(self):
        self.recorder = AudioRecorder(duration=3)
        self.processor = VoiceProcessor()
        self.verifier = SpeakerVerifier()
        self.passphrase = "Open my secure vault"
        self.passwords = {}  # Dictionary to store user passwords
        
    def enroll_user(self, user_id):
        """Enroll a new user by recording multiple samples of the passphrase and setting a password."""
        print(f"\n=== Enrolling User: {user_id} ===")
        
        # Set password
        password = input("Set your password: ")
        self.passwords[user_id] = password
        
        # Voice enrollment
        print(f"\nNow, please say the passphrase: '{self.passphrase}'")
        print("You will need to record this 3 times.")
        
        recordings = []
        for i in range(3):
            input(f"\nPress Enter to start recording {i+1}/3...")
            self.recorder.record_audio()
            filename = f"{user_id}_enroll_{i+1}.wav"
            filepath = self.recorder.save_recording(filename)
            recordings.append(filepath)
            
        # Process recordings and train model
        features = self.processor.process_enrollment_samples(recordings)
        self.verifier.train_model(user_id, features)
        
        print(f"\nUser {user_id} has been successfully enrolled!")
        
    def verify_user(self, user_id):
        """Verify a user's identity using either voice or password."""
        print(f"\n=== Verifying User: {user_id} ===")
        print("Choose verification method:")
        print("1. Voice Verification")
        print("2. Password Verification")
        
        choice = input("Enter your choice (1-2): ")
        
        if choice == "1":
            self._verify_voice(user_id)
        elif choice == "2":
            self._verify_password(user_id)
        else:
            print("Invalid choice!")
            
    def _verify_voice(self, user_id):
        """Verify user using voice."""
        print(f"\nPlease say the passphrase: '{self.passphrase}'")
        
        input("Press Enter to start recording...")
        self.recorder.record_audio()
        filename = f"{user_id}_verify.wav"
        filepath = self.recorder.save_recording(filename)
        
        # Process recording and verify
        features = self.processor.process_verification_sample(filepath)
        is_verified, score = self.verifier.verify_speaker(user_id, features)
        
        if is_verified:
            print("\n✅ Voice Verification Successful!")
            print(f"Verification Score: {score:.2f}")
            self._simulate_vault_opening()
        else:
            print("\n❌ Voice Verification Failed!")
            print(f"Verification Score: {score:.2f}")
            
    def _verify_password(self, user_id):
        """Verify user using password."""
        if user_id not in self.passwords:
            print("\n❌ User not found!")
            return
            
        password = input("Enter your password: ")
        
        if password == self.passwords[user_id]:
            print("\n✅ Password Verification Successful!")
            self._simulate_vault_opening()
        else:
            print("\n❌ Password Verification Failed!")
            
    def _simulate_vault_opening(self):
        """Simulate the vault opening process."""
        print("\nOpening vault...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        print("Vault is now open!")
        
    def list_enrolled_users(self):
        """Display all enrolled users."""
        users = self.verifier.list_users()
        if users:
            print("\nEnrolled Users:")
            for user in users:
                print(f"- {user}")
        else:
            print("\nNo users are currently enrolled.")
            
    def delete_user(self, user_id):
        """Delete a user's voice model and password."""
        self.verifier.delete_model(user_id)
        if user_id in self.passwords:
            del self.passwords[user_id]
        print(f"\nUser {user_id} has been deleted.")

def main():
    system = BankVaultSystem()
    
    while True:
        print("\n=== Voice/Password-Activated Bank Vault System ===")
        print("1. Enroll New User")
        print("2. Verify User")
        print("3. List Enrolled Users")
        print("4. Delete User")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            user_id = input("Enter user ID: ")
            system.enroll_user(user_id)
            
        elif choice == "2":
            user_id = input("Enter user ID: ")
            system.verify_user(user_id)
            
        elif choice == "3":
            system.list_enrolled_users()
            
        elif choice == "4":
            user_id = input("Enter user ID to delete: ")
            system.delete_user(user_id)
            
        elif choice == "5":
            print("\nThank you for using the Voice/Password-Activated Bank Vault System!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 