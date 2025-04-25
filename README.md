# Voice Vault

A secure banking verification system using voice recognition and advanced password protection. The system provides a modern, user-friendly interface with multiple security features.

## Project Overview

![image](https://github.com/user-attachments/assets/cbc52d3c-bf03-4c77-aa20-d98c481f75cf)

Voice Vault is a secure banking application that combines traditional password verification with biometric voice authentication. The application features a modern, user-friendly interface with a focus on security and reliability.

## Key Features

- **Dual Authentication System**: Use either password or voice for verification
- **Secure Data Storage**: User data is stored securely
- **New User Registration**: Create a new account with voice verification
- **Deposit & Withdrawal**: Easily manage your balance
- **Voice Verification System**: Authenticate using your voice
- **Modern User Interface**: Sleek and easy-to-use design

## Screenshots

### Signin Screen
![image](https://github.com/user-attachments/assets/90945d11-1f98-49ed-9ef2-d6d66ab3ace3)


### Voice Authentication
![image](https://github.com/user-attachments/assets/7ada9dd8-7d54-4209-88e6-087df338219e)

### Account Window
![image](https://github.com/user-attachments/assets/686adb24-ed2e-4264-8095-3f9a378cadfd)

### Transactions Window
![image](https://github.com/user-attachments/assets/ff3d6000-1588-4ac6-8b25-7dff90e2f9c2)

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

![image](https://github.com/user-attachments/assets/c338864f-5e36-4f73-83c9-c484725f09e3)

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
