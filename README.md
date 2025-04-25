# Voice Vault

A secure banking verification system using voice recognition and advanced password protection. The system provides a modern, user-friendly interface with multiple security features.

## Project Overview

![System Screenshot](screenshots/main_screen.png)

Voice Vault is a secure banking application that combines traditional password verification with biometric voice authentication. The application features a modern, user-friendly interface with a focus on security and reliability.

## Key Features

- **Dual Authentication System**: Use either password or voice for verification
- **Secure Data Storage**: User data is stored securely
- **New User Registration**: Create a new account with voice verification
- **Deposit & Withdrawal**: Easily manage your balance
- **Voice Verification System**: Authenticate using your voice
- **Modern User Interface**: Sleek and easy-to-use design

## Screenshots

### Login Screen
![Login Screen](screenshots/login_screen.png)

### User Dashboard
![User Dashboard](screenshots/dashboard.png)

### Voice Authentication
![Voice Authentication](screenshots/voice_auth.png)

### Deposit Window
![Deposit Window](screenshots/deposit.png)

## Requirements

- Python 3.8 or higher
- Required libraries listed in `requirements.txt`

## Installation

1. Download the project
2. Install required libraries:
```
pip install -r requirements.txt
```

## How to Run

To run the application, execute:
```
python gui.py
```

## Project Structure

- `gui.py`: Main graphical user interface
- `main.py`: Core verification and authentication system
- `audio_recorder.py`: Handles audio recording
- `voice_processor.py`: Processes audio signals
- `speaker_verifier.py`: Speaker verification system
- `bank_vault_data.json`: User data storage file

## System Architecture

![System Architecture](screenshots/system_architecture.png)

1. **Dual Authentication**: Users can choose to verify using password or voice
2. **Voice Processing**: Voice is recorded, processed, and features are extracted
3. **Matching**: Voice sample is compared to stored samples to verify user identity
4. **Security**: System locks after several failed attempts to prevent breaches

## Future Development

The project can be developed in the following ways:
- Add more authentication methods such as fingerprint or facial recognition
- Improve voice recognition algorithms
- Add more banking features
- Enhance security against cyber attacks

## License

This project is open source and is licensed under the MIT License. 