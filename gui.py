import customtkinter as ctk
from PIL import Image, ImageTk
import os
import time
import threading
import winsound
import re
from main import BankVaultSystem
from tkinter import filedialog
import tkinter as tk
import random
import json  # For saving and loading data

class BankVaultGUI:
    def create_default_profile_image(self, size=100):
        """Create a default profile image with random color"""
        img = Image.new('RGB', (size, size), color=(
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        ))
        
        # Add first letter of "User" in the center
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", size=40)
        except:
            font = ImageFont.load_default()
            
        draw.text((size/2-10, size/2-20), "U", fill="white", font=font)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    
    def __init__(self):
        self.system = BankVaultSystem()
        
        # Configure the main window
        self.root = ctk.CTk()
        self.root.title("Voice Vault")  # Change project name
        
        # Set window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set application icon
        try:
            icon_path = "icone.ico"  # Use the existing icone.ico file
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print("Application icon set successfully.")
            else:
                print(f"Icon file not found at {icon_path}. Using default icon.")
                # Fallback to icon.png if ico file is not found
                png_icon_path = "icon.png"
                if os.path.exists(png_icon_path):
                    icon_img = Image.open(png_icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_img)
                    self.root.iconphoto(True, icon_photo)
                    print("Application icon set using PNG format.")
        except Exception as e:
            print(f"Error setting application icon: {e}")
        
        # Make the window responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Set window size and center it
        window_width = 900
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ensure the window is resizable
        self.root.minsize(800, 600)  # Minimum size
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Define color scheme - dark theme
        self.colors = {
            "primary": "#1E88E5",      # Blue
            "secondary": "#7E57C2",    # Purple
            "success": "#43A047",      # Green 
            "warning": "#FFA000",      # Orange
            "danger": "#E53935",       # Red
            "background": "#121212",   # Dark background
            "card": "#1E1E1E",         # Card background
            "card_alt": "#2D2D2D",     # Alternate card background
            "text": "#FFFFFF",         # White text
            "text_alt": "#AAAAAA",     # Secondary text color
            "success_bg": "#E8F5E9"    # Light green background
        }
        
        # List of hints to display
        self.hints = [
            "Tip: Keep your password secure!",
            "Tip: Never share your account details with anyone.",
            "Tip: Regular deposits help grow your savings.",
            "Tip: Check your balance regularly.",
            "Tip: You can use your email or phone to login.",
            "Tip: Voice authentication adds an extra layer of security.",
            "Tip: Update your contact information when it changes.",
            "Tip: Use a strong password with mixed characters.",
            "Tip: Sign out when using shared computers."
        ]
        
        # Path for voice samples directory
        self.voice_samples_dir = "voice_samples"
        # Create the directory if it doesn't exist
        if not os.path.exists(self.voice_samples_dir):
            os.makedirs(self.voice_samples_dir)
        
        # Initialize current_hint attribute
        self.current_hint = self.hints[0]
        self.hint_label = None
        
        # Set default profile picture
        self.default_profile_pic = self.create_default_profile_image()
        self.user_profile_pic = self.default_profile_pic
        
        # File to save user data
        self.data_file = "bank_vault_data.json"
        
        # Load saved data if it exists
        self.load_user_data()
        
        # Create main frame with grid instead of pack for responsiveness
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Store current window
        self.current_window = None
        self.current_user = None
        
        # Show login screen
        self.show_login_screen()
        
        # Start hint rotation
        self.rotate_hints()
    
    def load_user_data(self):
        """Load user data from file"""
        # Default data if no file exists
        self.users_db = {
            "user1": {
                "full_name": "Ahmed Mohamed",
                "username": "user1",
                "email": "ahmed@example.com",
                "phone": "+201234567890",
                "password": "password1",
                "balance": 25000.50,
                "vault_status": "Active",
                "profile_pic": None
            },
            "user2": {
                "full_name": "Sara Ali",
                "username": "user2", 
                "email": "sara@example.com",
                "phone": "+201122334455",
                "password": "password2",
                "balance": 10500.75,
                "vault_status": "Active",
                "profile_pic": None
            }
        }
        
        try:
            # Try to read the file if it exists
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as file:
                    loaded_data = json.load(file)
                    self.users_db = loaded_data
                    print(f"Loaded {len(self.users_db)} users from database file.")
        except Exception as e:
            print(f"Error loading data: {e}")
            # Loading failed, use default data
            pass
    
    def save_user_data(self):
        """Save user data to file"""
        try:
            with open(self.data_file, 'w') as file:
                # Convert data to JSON format and save it
                json.dump(self.users_db, file, indent=4)
                print(f"Saved {len(self.users_db)} users to database file.")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def rotate_hints(self):
        """Rotate through different hints every 5 seconds"""
        # Get a new random hint that's different from the current one
        available_hints = [hint for hint in self.hints if hint != self.current_hint]
        new_hint = random.choice(available_hints)
        self.current_hint = new_hint
        
        # Update the hint label if it exists
        if hasattr(self, 'hint_label') and self.hint_label:
            self._animate_label(self.hint_label, self.current_hint, self.colors["primary"])
        
        # Schedule the next hint update
        self.root.after(5000, self.rotate_hints)
    
    def _animate_label(self, label, text, color=None):
        """Animate label with text fade effect"""
        if color is None:
            color = self.colors["primary"]
            
        label.configure(text_color="#357abd")
        label.configure(text=text)
        self.root.after(100, lambda: label.configure(text_color=color))
    
    def _play_sound(self, sound_type):
        """Play a sound effect"""
        try:
            if sound_type == "click":
                winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
            elif sound_type == "success":
                winsound.PlaySound("SystemAsterisk", winsound.SND_ASYNC)
            elif sound_type == "error":
                winsound.PlaySound("SystemHand", winsound.SND_ASYNC)
        except:
            # If sound fails, just skip it
            pass
            
    def _animate_button(self, button, callback=None):
        """Animate button click with color change"""
        original_color = button._fg_color
        button.configure(fg_color=self.colors["secondary"])
        self._play_sound("click")
        
        # Change back after a short delay
        def reset_color():
            button.configure(fg_color=original_color)
            if callback:
                callback()
                
        self.root.after(100, reset_color)
        
    def button_with_animation(self, button, callback):
        """Wrapper to add animation to button clicks"""
        def animated_callback():
            self._animate_button(button, callback)
            
        return animated_callback
    
    def sign_in(self):
        """Sign in the user with the provided credentials"""
        identifier = self.login_entry.get()
        password = self.password_entry.get()
        
        # Validate inputs
        if not identifier or not password:
            self._animate_label(self.status_label, "⚠️ Please enter both identifier and password", self.colors["danger"])
            self._play_sound("error")
            return
            
        # Check credentials against our mock database
        found_user = None
        for username, user_data in self.users_db.items():
            if (username == identifier or 
                user_data.get("email") == identifier or 
                user_data.get("phone") == identifier):
                
                if user_data.get("password") == password:  # Simple password check
                    found_user = user_data
                    found_user["username"] = username  # Add username to data
                    break
        
        if found_user:
            self._play_sound("success")
            self.current_user = found_user
            self.show_user_dashboard()
        else:
            self._animate_label(self.status_label, "❌ Invalid credentials", self.colors["danger"])
            self._play_sound("error")
    
    def show_signup_window(self):
        """Show the signup window"""
        # Hide current window
        if self.current_window:
            self.current_window.pack_forget()
        
        # Create signup window
        signup_window = ctk.CTkFrame(self.main_frame, fg_color=self.colors["card"], corner_radius=15)
        signup_window.pack(pady=20, padx=20, fill="both", expand=True)
        self.current_window = signup_window
        
        # Title
        ctk.CTkLabel(
            signup_window,
            text="Create New Account",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=20)
        
        # Create scrollable frame for form fields
        form_frame = ctk.CTkScrollableFrame(signup_window, fg_color="transparent")
        form_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
        # Full Name entry
        ctk.CTkLabel(form_frame, text="Full Name:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        full_name_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        full_name_entry.pack(pady=(5, 15), fill="x")
        
        # Username entry
        ctk.CTkLabel(form_frame, text="Username:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        username_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        username_entry.pack(pady=(5, 15), fill="x")
        
        # Email entry
        ctk.CTkLabel(form_frame, text="Email:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        email_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        email_entry.pack(pady=(5, 15), fill="x")
        
        # Phone entry
        ctk.CTkLabel(form_frame, text="Phone:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        phone_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        phone_entry.pack(pady=(5, 15), fill="x")
        
        # Vault Details section
        ctk.CTkLabel(form_frame, text="Vault Details:", font=("Helvetica", 16, "bold"), text_color=self.colors["primary"]).pack(pady=(15, 5), anchor="w")
        
        # Vault Type
        ctk.CTkLabel(form_frame, text="Vault Type:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        vault_type_var = tk.StringVar(value="Standard")
        vault_type_combobox = ctk.CTkComboBox(
            form_frame,
            values=["Standard", "Premium", "VIP"],
            variable=vault_type_var,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        vault_type_combobox.pack(pady=(5, 15), fill="x")
        
        # Initial Deposit
        ctk.CTkLabel(form_frame, text="Initial Deposit ($):", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        initial_deposit_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"],
            placeholder_text="0.00"
        )
        initial_deposit_entry.pack(pady=(5, 15), fill="x")
        
        # Password entry with visibility toggle
        ctk.CTkLabel(form_frame, text="Password:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        
        # Password hint
        password_hint_label = ctk.CTkLabel(
            form_frame,
            text="Password must include: uppercase letters, numbers, symbols, and be at least 8 characters",
            font=("Helvetica", 12),
            text_color=self.colors["text_alt"],
            wraplength=300
        )
        password_hint_label.pack(pady=(0, 5), anchor="w")
        
        # Password frame to hold entry and toggle button
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(pady=(5, 15), fill="x")
        password_frame.grid_columnconfigure(0, weight=1)
        password_frame.grid_columnconfigure(1, weight=0)
        
        password_entry = ctk.CTkEntry(
            password_frame,
            show="•",
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        password_entry.grid(row=0, column=0, sticky="ew")
        
        # Password visibility toggle
        password_visible = [False]  # Use list to be mutable in the closure
        
        def toggle_password_visibility():
            password_visible[0] = not password_visible[0]
            if password_visible[0]:
                password_entry.configure(show="")
                confirm_pass_entry.configure(show="")
                password_toggle_btn.configure(text="👁️")
            else:
                password_entry.configure(show="•")
                confirm_pass_entry.configure(show="•")
                password_toggle_btn.configure(text="👁️‍🗨️")
        
        password_toggle_btn = ctk.CTkButton(
            password_frame,
            text="👁️‍🗨️",
            command=toggle_password_visibility,
            width=40,
            height=40,
            font=("Helvetica", 16),
            fg_color=self.colors["card_alt"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        password_toggle_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Password strength checker as user types
        def check_password_strength(*args):
            current_password = password_entry.get()
            
            has_upper = bool(re.search(r'[A-Z]', current_password))
            has_digit = bool(re.search(r'[0-9]', current_password))
            has_symbol = bool(re.search(r'[!@#$%^&*(),.?\":{}|<>]', current_password))
            has_length = len(current_password) >= 8
            
            if not current_password:
                password_hint_label.configure(
                    text="Password must include: uppercase letters, numbers, symbols, and be at least 8 characters",
                    text_color=self.colors["text_alt"]
                )
                return
                
            # Create password strength message
            message = "Password requirements: "
            missing_requirements = []
            
            if not has_upper:
                missing_requirements.append("uppercase letters")
            if not has_digit:
                missing_requirements.append("numbers")
            if not has_symbol:
                missing_requirements.append("symbols")
            if not has_length:
                missing_requirements.append("at least 8 characters")
                
            if missing_requirements:
                message += ", ".join(missing_requirements)
                password_hint_label.configure(text=message, text_color=self.colors["warning"])
            else:
                password_hint_label.configure(text="Strong password! ✅", text_color=self.colors["success"])
        
        # Track password changes
        password_var = tk.StringVar()
        password_entry.configure(textvariable=password_var)
        password_var.trace_add("write", check_password_strength)
        
        # Confirm Password entry
        ctk.CTkLabel(form_frame, text="Confirm Password:", font=("Helvetica", 14), text_color=self.colors["text"]).pack(pady=(5, 0), anchor="w")
        confirm_pass_entry = ctk.CTkEntry(
            form_frame,
            show="•",
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        confirm_pass_entry.pack(pady=(5, 15), fill="x")
        
        # Voice Authentication Section
        ctk.CTkLabel(form_frame, text="Voice Authentication Setup:", font=("Helvetica", 16, "bold"), text_color=self.colors["primary"]).pack(pady=(15, 5), anchor="w")
        
        ctk.CTkLabel(
            form_frame,
            text="You need to record your voice 3 times for authentication setup.",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        ).pack(pady=(5, 10))
        
        # Voice recording status
        voice_status_frame = ctk.CTkFrame(form_frame, fg_color=self.colors["card_alt"], corner_radius=8)
        voice_status_frame.pack(pady=10, fill="x")
        
        voice_recordings = [False, False, False]  # Track completion of each recording
        
        # Recording status indicators
        recording_status_frame = ctk.CTkFrame(voice_status_frame, fg_color="transparent")
        recording_status_frame.pack(pady=10, padx=10, fill="x")
        
        recording_labels = []
        recording_buttons = []
        
        for i in range(3):
            frame = ctk.CTkFrame(recording_status_frame, fg_color="transparent")
            frame.pack(side="left", expand=True, fill="x", padx=5)
            
            label = ctk.CTkLabel(
                frame,
                text=f"Recording {i+1}",
                font=("Helvetica", 12),
                text_color=self.colors["text_alt"]
            )
            label.pack(side="top")
            
            status = ctk.CTkLabel(
                frame,
                text="❌ Not Recorded",
                font=("Helvetica", 12, "bold"),
                text_color=self.colors["danger"]
            )
            status.pack(side="top", pady=5)
            
            # Add individual record button for each recording
            record_btn = ctk.CTkButton(
                frame,
                text="Record",
                command=lambda idx=i: record_voice_for_signup(idx),
                font=("Helvetica", 12),
                fg_color=self.colors["primary"],
                hover_color=self.colors["secondary"],
                corner_radius=8,
                width=80,
                height=30
            )
            record_btn.pack(side="top", pady=5)
            
            recording_labels.append(status)
            recording_buttons.append(record_btn)
        
        # Function to record voice
        def record_voice_for_signup(recording_index):
            if recording_index >= 3:
                return
                
            # Create recording dialog
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Voice Recording")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Dialog content
            ctk.CTkLabel(
                dialog,
                text=f"Recording {recording_index + 1} of 3",
                font=("Helvetica", 18, "bold"),
                text_color=self.colors["primary"]
            ).pack(pady=(20, 10))
            
            instruction_label = ctk.CTkLabel(
                dialog,
                text="Please say: 'My voice is my password'",
                font=("Helvetica", 14),
                text_color=self.colors["text"]
            )
            instruction_label.pack(pady=10)
            
            # Progress bar
            progress = ctk.CTkProgressBar(dialog, width=300)
            progress.pack(pady=10)
            progress.set(0)
            
            # Status label
            status_label = ctk.CTkLabel(
                dialog,
                text="Click 'Start Recording' when ready...",
                font=("Helvetica", 14),
                text_color=self.colors["text"]
            )
            status_label.pack(pady=10)
            
            # Recording state
            recording_active = [False]
            recording_completed = [False]
            recording_filename = [None]  # To store the recording filename
            
            def start_recording():
                if recording_completed[0]:
                    return
                    
                recording_active[0] = True
                start_btn.configure(state="disabled")
                self._play_sound("click")
                
                status_label.configure(text="Recording... Please speak now.")
                
                # In a real application, we would record the voice here
                # For testing, we simulate the recording process
                
                # Create a unique filename for the recording
                username = username_entry.get()
                timestamp = int(time.time())
                filename = f"{username}_sample_{recording_index+1}_{timestamp}.wav"
                full_path = os.path.join(self.voice_samples_dir, filename)
                recording_filename[0] = full_path
                
                # Simulate recording with progress bar
                def update_progress(value):
                    if not recording_active[0]:
                        return
                        
                    progress.set(value)
                    if value < 1.0:
                        dialog.after(300, lambda: update_progress(value + 0.1))
                    else:
                        recording_active[0] = False
                        recording_completed[0] = True
                        status_label.configure(text="Recording complete! Confirm or re-record.")
                        self._play_sound("success")
                        
                        # Simulate saving the audio file (in a real app there would be actual audio data)
                        with open(full_path, 'wb') as f:
                            f.write(b'DUMMY_VOICE_DATA')  # Dummy data for testing
                        
                        # Enable buttons
                        start_btn.configure(text="Re-record", state="normal")
                        confirm_btn.configure(state="normal")
                
                # Start progress
                update_progress(0)
            
            def confirm_recording():
                if not recording_completed[0]:
                    return
                    
                voice_recordings[recording_index] = True
                
                # Save filename in list next to username for later verification
                if not hasattr(form_frame, 'voice_sample_files'):
                    form_frame.voice_sample_files = [None, None, None]
                form_frame.voice_sample_files[recording_index] = recording_filename[0]
                
                recording_labels[recording_index].configure(
                    text="✅ Recorded",
                    text_color=self.colors["success"]
                )
                recording_buttons[recording_index].configure(
                    text="Re-record",
                    fg_color=self.colors["card_alt"]
                )
                self._play_sound("success")
                dialog.destroy()
            
            def cancel_recording():
                recording_active[0] = False
                dialog.destroy()
            
            # Buttons
            buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            buttons_frame.pack(pady=10)
            
            start_btn = ctk.CTkButton(
                buttons_frame,
                text="Start Recording",
                command=start_recording,
                width=120,
                height=35,
                font=("Helvetica", 14),
                fg_color=self.colors["primary"],
                hover_color=self.colors["secondary"],
                corner_radius=8
            )
            start_btn.pack(side="left", padx=5)
            
            confirm_btn = ctk.CTkButton(
                buttons_frame,
                text="Confirm",
                command=confirm_recording,
                width=100,
                height=35,
                state="disabled",
                font=("Helvetica", 14),
                fg_color=self.colors["success"],
                hover_color="#2E7D32",
                corner_radius=8
            )
            confirm_btn.pack(side="left", padx=5)
            
            ctk.CTkButton(
                buttons_frame,
                text="Cancel",
                command=cancel_recording,
                width=80,
                height=35,
                font=("Helvetica", 14),
                fg_color=self.colors["background"],
                hover_color=self.colors["secondary"],
                border_width=1,
                border_color=self.colors["primary"],
                text_color=self.colors["text"],
                corner_radius=8
            ).pack(side="left", padx=5)
        
        # Status label
        status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Helvetica", 14),
            text_color=self.colors["danger"]
        )
        status_label.pack(pady=10)
        
        def sign_up():
            full_name = full_name_entry.get()
            username = username_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            password = password_entry.get()
            confirm_password = confirm_pass_entry.get()
            vault_type = vault_type_var.get()
            
            # Get initial deposit
            try:
                initial_deposit = float(initial_deposit_entry.get()) if initial_deposit_entry.get() else 0.0
            except ValueError:
                self._animate_label(status_label, "⚠️ Initial deposit must be a valid number", self.colors["danger"])
                self._play_sound("error")
                return
            
            # Validate inputs
            if not all([full_name, username, email, phone, password, confirm_password]):
                self._animate_label(status_label, "⚠️ All fields are required", self.colors["danger"])
                self._play_sound("error")
                return
            
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                self._animate_label(status_label, "⚠️ Invalid email format", self.colors["danger"])
                self._play_sound("error")
                return
            
            # Validate phone format - must be exactly 11 digits
            if not re.match(r"^\+?[0-9]{11}$", phone):
                self._animate_label(status_label, "⚠️ Phone number must be exactly 11 digits", self.colors["danger"])
                self._play_sound("error")
                return
            
            # Validate password complexity
            if not (re.search(r"[A-Z]", password) and  # At least one uppercase letter
                    re.search(r"[0-9]", password) and  # At least one digit
                    re.search(r"[!@#$%^&*(),.?\":{}|<>]", password) and  # At least one special character
                    len(password) >= 8):  # Minimum length
                self._animate_label(
                    status_label, 
                    "⚠️ Password must contain at least 8 characters including uppercase, numbers, and symbols", 
                    self.colors["danger"]
                )
                self._play_sound("error")
                return
            
            # Check if passwords match
            if password != confirm_password:
                self._animate_label(status_label, "⚠️ Passwords don't match", self.colors["danger"])
                self._play_sound("error")
                return
                
            # Check if all voice recordings are completed
            if not all(voice_recordings):
                self._animate_label(status_label, "⚠️ Please complete all voice recordings", self.colors["danger"])
                self._play_sound("error")
                return
            
            # Check if username/email/phone already exists
            for existing_user, user_data in self.users_db.items():
                if (existing_user == username or 
                    user_data.get("email") == email or 
                    user_data.get("phone") == phone):
                    
                    self._animate_label(
                        status_label, 
                        "⚠️ Username, email or phone already exists. Would you like to login?", 
                        self.colors["warning"]
                    )
                    self._play_sound("error")
                    return
            
            # Create new user
            self.users_db[username] = {
                "full_name": full_name,
                "username": username,
                "email": email,
                "phone": phone,
                "password": password,
                "balance": initial_deposit,
                "vault_type": vault_type,
                "vault_status": "Active",
                "profile_pic": None,
                "voice_authenticated": True,
                "voice_samples": []
            }
            
            # Add voice sample paths if available
            if hasattr(form_frame, 'voice_sample_files'):
                for sample_path in form_frame.voice_sample_files:
                    if sample_path:
                        # Store just the filename instead of the full path
                        filename = os.path.basename(sample_path)
                        self.users_db[username]["voice_samples"].append(filename)
            
            # Save data after creating new user
            self.save_user_data()
            
            # Show success message
            self._animate_label(status_label, "✅ Account created successfully!", self.colors["success"])
            self._play_sound("success")
            
            # Redirect to login
            signup_window.after(2000, self.show_login_screen)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(signup_window, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        # Sign Up button
        ctk.CTkButton(
            buttons_frame,
            text="Create Account",
            command=sign_up,
            width=150,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        ).pack(side="left", padx=10)
        
        # Back button
        ctk.CTkButton(
            buttons_frame,
            text="Back",
            command=self.show_login_screen,
            width=150,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            hover_color=self.colors["secondary"],
            border_width=1,
            border_color=self.colors["primary"],
            corner_radius=8
        ).pack(side="left", padx=10)
    
    def show_user_dashboard(self):
        """Show the user dashboard"""
        self._hide_main_window()
        
        # Create the dashboard frame
        dashboard = ctk.CTkFrame(self.main_frame, fg_color=self.colors["card"], corner_radius=15)
        dashboard.pack(pady=20, padx=20, fill="both", expand=True)
        self.current_window = dashboard
        
        # Configure grid for responsiveness
        dashboard.grid_columnconfigure(0, weight=1)
        dashboard.grid_columnconfigure(1, weight=1)
        dashboard.grid_rowconfigure(0, weight=0)  # Header
        dashboard.grid_rowconfigure(1, weight=1)  # Content
        dashboard.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header with welcome message and logout button
        header_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 0))
        
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Welcome, {self.current_user.get('full_name', 'User')}!",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors["primary"]
        )
        welcome_label.pack(side="left", pady=10)
        
        logout_button = ctk.CTkButton(
            header_frame,
            text="Logout",
            command=self.sign_out,
            width=100,
            font=("Helvetica", 14),
            fg_color=self.colors["danger"],
            hover_color="#ff3333",
            corner_radius=8
        )
        logout_button.pack(side="right", pady=10)
        
        # Create tabs for different sections
        tabview = ctk.CTkTabview(dashboard, fg_color=self.colors["background"])
        tabview.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        
        # Add tabs
        tab_account = tabview.add("Account")
        tab_vault = tabview.add("Vault")
        tab_transactions = tabview.add("Transactions")
        
        # Configure tabs for responsiveness
        for tab in [tab_account, tab_vault, tab_transactions]:
            tab.grid_columnconfigure(0, weight=1)
        
        # Account Tab Content
        account_frame = ctk.CTkFrame(tab_account, fg_color="transparent")
        account_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # User info section
        user_info_frame = ctk.CTkFrame(account_frame, fg_color=self.colors["card_alt"], corner_radius=10)
        user_info_frame.pack(fill="x", padx=10, pady=10)
        
        # Profile picture (placeholder)
        profile_pic_frame = ctk.CTkFrame(user_info_frame, width=100, height=100, corner_radius=50, fg_color=self.colors["primary"])
        profile_pic_frame.pack(side="left", padx=20, pady=20)
        
        profile_initial = ctk.CTkLabel(
            profile_pic_frame,
            text=self.current_user.get('full_name', 'U')[0],
            font=("Helvetica", 36, "bold"),
            text_color="white"
        )
        profile_initial.place(relx=0.5, rely=0.5, anchor="center")
        
        # User details
        user_details_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        user_details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=20)
        
        ctk.CTkLabel(
            user_details_frame,
            text=f"Name: {self.current_user.get('full_name', 'Unknown')}",
            font=("Helvetica", 16),
            anchor="w",
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(
            user_details_frame,
            text=f"Username: {self.current_user.get('username', 'Unknown')}",
            font=("Helvetica", 16),
            anchor="w",
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(
            user_details_frame,
            text=f"Email: {self.current_user.get('email', 'Unknown')}",
            font=("Helvetica", 16),
            anchor="w",
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(
            user_details_frame,
            text=f"Phone: {self.current_user.get('phone', 'Unknown')}",
            font=("Helvetica", 16),
            anchor="w",
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=5)
        
        # Account balance
        balance_frame = ctk.CTkFrame(account_frame, fg_color=self.colors["success_bg"], corner_radius=10)
        balance_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        ctk.CTkLabel(
            balance_frame,
            text="Current Balance",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["success"]
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            balance_frame,
            text=f"${self.current_user.get('balance', 0):.2f}",
            font=("Helvetica", 30, "bold"),
            text_color=self.colors["success"]
        ).pack(pady=(0, 15))
        
        # Quick actions
        actions_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=10)
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        deposit_button = ctk.CTkButton(
            actions_frame,
            text="Deposit",
            command=self.show_deposit_dialog,
            width=150,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        deposit_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        withdraw_button = ctk.CTkButton(
            actions_frame,
            text="Withdraw",
            command=self.show_withdraw_dialog,
            width=150,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        withdraw_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Vault Tab Content
        vault_frame = ctk.CTkFrame(tab_vault, fg_color="transparent")
        vault_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Vault status
        vault_status_frame = ctk.CTkFrame(vault_frame, fg_color=self.colors["card_alt"], corner_radius=10)
        vault_status_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            vault_status_frame,
            text="Vault Status",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(15, 5))
        
        status_color = self.colors["success"] if self.current_user.get('vault_status') == "Active" else self.colors["danger"]
        
        ctk.CTkLabel(
            vault_status_frame,
            text=f"{self.current_user.get('vault_status', 'Unknown')}",
            font=("Helvetica", 20, "bold"),
            text_color=status_color
        ).pack(pady=(0, 15))
        
        # Voice authentication section
        voice_auth_frame = ctk.CTkFrame(vault_frame, fg_color=self.colors["card_alt"], corner_radius=10)
        voice_auth_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        ctk.CTkLabel(
            voice_auth_frame,
            text="Voice Authentication",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            voice_auth_frame,
            text="Use voice recognition to access your vault",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        ).pack(pady=5)
        
        record_button = ctk.CTkButton(
            voice_auth_frame,
            text="Record Voice",
            command=self.record_voice,
            width=200,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        record_button.pack(pady=15)
        
        # Transactions Tab Content
        trans_frame = ctk.CTkFrame(tab_transactions, fg_color="transparent")
        trans_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            trans_frame,
            text="Recent Transactions",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(0, 10))
        
        # Mock transactions list
        transactions = [
            {"type": "Deposit", "amount": 500, "date": "2023-11-10"},
            {"type": "Withdrawal", "amount": 200, "date": "2023-11-12"},
            {"type": "Deposit", "amount": 1000, "date": "2023-11-15"}
        ]
        
        # Transactions list
        for tx in transactions:
            tx_frame = ctk.CTkFrame(trans_frame, fg_color=self.colors["card_alt"], corner_radius=5)
            tx_frame.pack(fill="x", padx=10, pady=5)
            
            tx_type_color = self.colors["success"] if tx["type"] == "Deposit" else self.colors["danger"]
            tx_amount_prefix = "+" if tx["type"] == "Deposit" else "-"
            
            tx_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            ctk.CTkLabel(
                tx_frame,
                text=tx["type"],
                font=("Helvetica", 14),
                text_color=tx_type_color
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            ctk.CTkLabel(
                tx_frame,
                text=f"{tx_amount_prefix}${tx['amount']:.2f}",
                font=("Helvetica", 14, "bold"),
                text_color=tx_type_color
            ).grid(row=0, column=1, padx=10, pady=10)
            
            ctk.CTkLabel(
                tx_frame,
                text=tx["date"],
                font=("Helvetica", 14),
                text_color=self.colors["text_alt"]
            ).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # Footer with version and hints
        footer_frame = ctk.CTkFrame(dashboard, fg_color="transparent", height=30)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            footer_frame,
            text="Bank Vault System v1.0",
            font=("Helvetica", 12),
            text_color=self.colors["text_alt"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            footer_frame,
            text=self.current_hint,
            font=("Helvetica", 12),
            text_color=self.colors["primary"]
        ).pack(side="right")
    
    def show_deposit_dialog(self):
        """Show dialog to deposit money"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Deposit")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Make it modal
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ctk.CTkLabel(
            dialog,
            text="Deposit Amount",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(20, 30))
        
        amount_var = tk.StringVar()
        amount_entry = ctk.CTkEntry(
            dialog,
            width=200,
            height=40,
            font=("Helvetica", 14),
            textvariable=amount_var,
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        amount_entry.pack(pady=10)
        
        # Status label
        status_label = ctk.CTkLabel(
            dialog,
            text="",
            font=("Helvetica", 14),
            text_color=self.colors["danger"]
        )
        status_label.pack(pady=10)
        
        def handle_deposit():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    self._animate_label(status_label, "⚠️ Amount must be greater than zero", self.colors["danger"])
                    self._play_sound("error")
                    return
                    
                # Update balance
                self.current_user['balance'] = self.current_user.get('balance', 0) + amount
                
                # Update in users_db
                username = self.current_user.get('username')
                if username in self.users_db:
                    self.users_db[username]['balance'] = self.current_user['balance']
                
                # Save data after deposit
                self.save_user_data()
                
                self._animate_label(status_label, f"✅ ${amount:.2f} deposited successfully!", self.colors["success"])
                self._play_sound("success")
                
                # Close dialog after delay and refresh dashboard
                dialog.after(2000, lambda: [dialog.destroy(), self.show_user_dashboard()])
                
            except ValueError:
                self._animate_label(status_label, "⚠️ Please enter a valid amount", self.colors["danger"])
                self._play_sound("error")
        
        # Buttons
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        ctk.CTkButton(
            buttons_frame,
            text="Deposit",
            command=handle_deposit,
            width=100,
            height=35,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            hover_color=self.colors["secondary"],
            border_width=1,
            border_color=self.colors["primary"],
            text_color=self.colors["text"],
            corner_radius=8
        ).pack(side="left", padx=10)
    
    def show_withdraw_dialog(self):
        """Show dialog to withdraw money"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Withdraw")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Make it modal
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ctk.CTkLabel(
            dialog,
            text="Withdraw Amount",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(20, 10))
        
        current_balance = self.current_user.get('balance', 0)
        ctk.CTkLabel(
            dialog,
            text=f"Current balance: ${current_balance:.2f}",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        ).pack(pady=(0, 20))
        
        amount_var = tk.StringVar()
        amount_entry = ctk.CTkEntry(
            dialog,
            width=200,
            height=40,
            font=("Helvetica", 14),
            textvariable=amount_var,
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        amount_entry.pack(pady=10)
        
        # Status label
        status_label = ctk.CTkLabel(
            dialog,
            text="",
            font=("Helvetica", 14),
            text_color=self.colors["danger"]
        )
        status_label.pack(pady=10)
        
        def handle_withdraw():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    self._animate_label(status_label, "⚠️ Amount must be greater than zero", self.colors["danger"])
                    self._play_sound("error")
                    return
                
                current_balance = self.current_user.get('balance', 0)
                if amount > current_balance:
                    self._animate_label(status_label, "⚠️ Insufficient funds", self.colors["danger"])
                    self._play_sound("error")
                    return
                    
                # Update balance
                self.current_user['balance'] = current_balance - amount
                
                # Update in users_db
                username = self.current_user.get('username')
                if username in self.users_db:
                    self.users_db[username]['balance'] = self.current_user['balance']
                
                # Save data after withdrawal
                self.save_user_data()
                
                self._animate_label(status_label, f"✅ ${amount:.2f} withdrawn successfully!", self.colors["success"])
                self._play_sound("success")
                
                # Close dialog after delay and refresh dashboard
                dialog.after(2000, lambda: [dialog.destroy(), self.show_user_dashboard()])
                
            except ValueError:
                self._animate_label(status_label, "⚠️ Please enter a valid amount", self.colors["danger"])
                self._play_sound("error")
        
        # Buttons
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        ctk.CTkButton(
            buttons_frame,
            text="Withdraw",
            command=handle_withdraw,
            width=100,
            height=35,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            hover_color=self.colors["secondary"],
            border_width=1,
            border_color=self.colors["primary"],
            text_color=self.colors["text"],
            corner_radius=8
        ).pack(side="left", padx=10)
    
    def record_voice(self):
        """Simulate voice recording for authentication"""
        # In a real app, this would record and process voice
        self._play_sound("click")
        
        # Create progress dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Voice Authentication")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Make it modal
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ctk.CTkLabel(
            dialog,
            text="Recording Voice...",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(20, 30))
        
        # Progress bar
        progress = ctk.CTkProgressBar(dialog, width=300)
        progress.pack(pady=10)
        progress.set(0)
        
        # Status label
        status_label = ctk.CTkLabel(
            dialog,
            text="Please speak clearly...",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        )
        status_label.pack(pady=10)
        
        # Simulate recording and processing
        def update_progress(value):
            progress.set(value)
            if value < 1.0:
                dialog.after(300, lambda: update_progress(value + 0.1))
            else:
                self._animate_label(status_label, "✅ Voice authenticated successfully!", self.colors["success"])
                self._play_sound("success")
                dialog.after(2000, dialog.destroy)
        
        # Start progress simulation
        dialog.after(500, lambda: update_progress(0.1))
    
    def show_login_screen(self):
        """Show the login screen"""
        # Clear any existing frames
        if self.current_window:
            self.current_window.pack_forget()
            
        # Create login frame
        login_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors["card"], corner_radius=15)
        login_frame.pack(pady=50, padx=50, fill="both", expand=True)
        self.current_window = login_frame
        
        # Create title with animation effect
        title_label = ctk.CTkLabel(
            login_frame,
            text="Elite Bank Vault System",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(30, 20))
        
        # Add subtitle with application status
        self.subtitle_label = ctk.CTkLabel(
            login_frame,
            text="Secure Access to Your Financial World",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Use a boolean to track current authentication method (voice is default)
        self.use_password_auth = False
        
        # Container for login fields (will contain either password or voice auth)
        self.login_container = ctk.CTkFrame(login_frame, fg_color="transparent")
        self.login_container.pack(pady=20, padx=30, fill="x")
        
        # Create both auth frames but show only one
        self.password_auth_frame = self.create_password_auth_frame()
        self.voice_auth_frame = self.create_voice_auth_frame()
        
        # Initially show voice authentication
        self.voice_auth_frame.pack(fill="x")
        
        # Authentication toggle button
        self.auth_toggle_btn = ctk.CTkButton(
            login_frame,
            text="Use Password Instead",
            command=self.toggle_auth_method,
            font=("Helvetica", 12),
            fg_color=self.colors["card_alt"],
            hover_color=self.colors["secondary"],
            corner_radius=8,
            width=200,
            height=35
        )
        self.auth_toggle_btn.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        # Login button with direct command
        login_btn = ctk.CTkButton(
            buttons_frame, 
            text="Login", 
            command=self.login,
            width=150, 
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        login_btn.pack(side="left", padx=10)
        
        # Sign Up button with direct command
        signup_btn = ctk.CTkButton(
            buttons_frame, 
            text="Sign Up", 
            command=self.show_signup_window,
            width=150, 
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            hover_color=self.colors["secondary"],
            border_width=1,
            border_color=self.colors["primary"],
            corner_radius=8
        )
        signup_btn.pack(side="left", padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            login_frame,
            text="",
            font=("Helvetica", 14),
            text_color=self.colors["danger"]
        )
        self.status_label.pack(pady=10)
        
        # Timer label for login lockout
        self.timer_label = ctk.CTkLabel(
            login_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            text_color=self.colors["warning"]
        )
        self.timer_label.pack(pady=(0, 10))
        
        # Counter variables for login attempts
        self.login_attempts = 3
        self.login_lockout = False
        self.lockout_timer = None
        
        # Footer
        footer_label = ctk.CTkLabel(
            login_frame,
            text="© 2024 Elite Bank. All rights reserved.",
            font=("Helvetica", 12),
            text_color="#888888"
        )
        footer_label.pack(pady=(20, 10))
        
        # Hints label
        self.hint_label = ctk.CTkLabel(
            login_frame,
            text=self.current_hint,
            font=("Helvetica", 12),
            text_color=self.colors["primary"]
        )
        self.hint_label.pack(pady=(0, 10))
    
    def create_password_auth_frame(self):
        """Create the password authentication frame"""
        frame = ctk.CTkFrame(self.login_container, fg_color="transparent")
        
        # Username/Email/Phone entry
        ctk.CTkLabel(
            frame,
            text="Username / Email / Phone:",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        ).pack(pady=(5, 0), anchor="w")
        
        self.login_entry = ctk.CTkEntry(
            frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        self.login_entry.pack(pady=(5, 15), fill="x")
        
        # Enable direct pasting
        self.enable_paste_for_entry(self.login_entry)
        
        # Password entry with show/hide toggle
        password_label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        password_label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            password_label_frame,
            text="Password:",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        ).pack(side="left")
        
        # Attempts counter
        self.attempts_label = ctk.CTkLabel(
            password_label_frame,
            text="Attempts remaining: 3",
            font=("Helvetica", 12),
            text_color=self.colors["text_alt"]
        )
        self.attempts_label.pack(side="right")
        
        # Password entry with eye icon inside
        password_entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        password_entry_frame.pack(pady=(5, 5), fill="x")
        
        # Create a custom entry with the eye icon inside
        # First, create a container frame that will hold both the entry and the button
        password_container = ctk.CTkFrame(
            password_entry_frame,
            fg_color=self.colors["background"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["primary"],
            height=40
        )
        password_container.pack(fill="x")
        password_container.pack_propagate(False)  # Prevent shrinking
        
        # Configure grid for the container
        password_container.columnconfigure(0, weight=1)  # Entry takes most space
        password_container.columnconfigure(1, weight=0)  # Button is fixed size
        
        # Password entry (no border since it's inside the container)
        self.password_entry = ctk.CTkEntry(
            password_container,
            show="•",
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_width=0,  # No border
            text_color=self.colors["text"]
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(10, 0))
        
        # Enable direct paste for the field
        self.enable_paste_for_entry(self.password_entry)
        
        # Password visibility toggle inside the entry
        password_visible = [False]
        
        def toggle_password_visibility():
            password_visible[0] = not password_visible[0]
            if password_visible[0]:
                self.password_entry.configure(show="")
                password_toggle_btn.configure(text="👁️")  # Eye icon
            else:
                self.password_entry.configure(show="•")
                password_toggle_btn.configure(text="👁️‍🗨️")  # Crossed eye icon
        
        password_toggle_btn = ctk.CTkButton(
            password_container,
            text="👁️‍🗨️",  # Start with crossed eye icon
            command=toggle_password_visibility,
            width=30,
            height=30,
            font=("Helvetica", 16),
            fg_color="transparent",  # Transparent to match entry
            hover_color=self.colors["background"],  # Same as background
            corner_radius=0,
            border_width=0
        )
        password_toggle_btn.grid(row=0, column=1, padx=(0, 5))
        
        return frame
        
    def enable_paste_for_entry(self, entry_widget):
        """Enable easy pasting for entry field"""
        # Bind custom keyboard shortcuts
        entry_widget.bind("<<Paste>>", lambda e: None)  # Prevent default event
        
        # Add Ctrl+V shortcut manually
        def paste_text(event=None):
            try:
                entry_widget.delete("sel.first", "sel.last")
            except:
                pass  # No text selected
                
            entry_widget.insert("insert", entry_widget.clipboard_get())
            return "break"  # Prevent default event
            
        # Bind keyboard shortcut
        entry_widget.bind("<Control-v>", paste_text)
        
        # Create context menu for entry field
        def show_context_menu(event):
            context_menu = tk.Menu(entry_widget, tearoff=0)
            context_menu.add_command(label="Cut", command=lambda: entry_widget.event_generate("<<Cut>>"))
            context_menu.add_command(label="Copy", command=lambda: entry_widget.event_generate("<<Copy>>"))
            context_menu.add_command(label="Paste", command=paste_text)
            context_menu.tk_popup(event.x_root, event.y_root)
            return "break"
            
        # Bind right mouse button click
        entry_widget.bind("<Button-3>", show_context_menu)
    
    def create_voice_auth_frame(self):
        """Create the voice authentication frame"""
        frame = ctk.CTkFrame(self.login_container, fg_color="transparent")
        
        # Voice authentication elements
        ctk.CTkLabel(
            frame,
            text="Username / Email / Phone:",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        ).pack(pady=(5, 0), anchor="w")
        
        self.voice_login_entry = ctk.CTkEntry(
            frame,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            border_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        self.voice_login_entry.pack(pady=(5, 15), fill="x")
        
        # Enable paste for voice entry field
        self.enable_paste_for_entry(self.voice_login_entry)
        
        # Add error message label for voice authentication interface
        self.voice_status_label = ctk.CTkLabel(
            frame,
            text="",
            font=("Helvetica", 14),
            text_color=self.colors["danger"]
        )
        self.voice_status_label.pack(pady=(0, 5))
        
        # Voice authentication button frame
        voice_button_frame = ctk.CTkFrame(frame, fg_color=self.colors["card_alt"], corner_radius=10)
        voice_button_frame.pack(pady=10, fill="x")
        
        voice_instruction = ctk.CTkLabel(
            voice_button_frame,
            text="Click the button below and say: 'My voice is my password'",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        )
        voice_instruction.pack(pady=(10, 5))
        
        # Modified: Remove remaining attempts label
        # in the main interface and replace with display in verification window only
        
        record_voice_button = ctk.CTkButton(
            voice_button_frame,
            text="Start Voice Authentication",
            command=self.authenticate_with_voice,
            width=200,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        record_voice_button.pack(pady=(5, 15))
        
        return frame
    
    def toggle_auth_method(self):
        """Toggle between voice and password authentication"""
        self.use_password_auth = not self.use_password_auth
        
        if self.use_password_auth:
            # Switch to password
            self.voice_auth_frame.pack_forget()
            self.password_auth_frame.pack(fill="x")
            self.auth_toggle_btn.configure(text="Use Voice Authentication")
        else:
            # Switch to voice
            self.password_auth_frame.pack_forget()
            self.voice_auth_frame.pack(fill="x")
            self.auth_toggle_btn.configure(text="Use Password Instead")
    
    def login(self):
        """Login with either password or voice authentication based on current mode"""
        if self.login_lockout:
            self._play_sound("error")
            return
            
        if self.use_password_auth:
            # Use password authentication
            identifier = self.login_entry.get()
            password = self.password_entry.get()
            self.login_with_password(identifier, password)
        else:
            # Voice authentication is handled separately by authenticate_with_voice
            pass
    
    def login_with_password(self, identifier, password):
        """Login with password authentication"""
        # Validate inputs
        if not identifier or not password:
            self._animate_label(self.status_label, "⚠️ Please enter both identifier and password", self.colors["danger"])
            self._play_sound("error")
            return
            
        # Check credentials against our mock database
        found_user = None
        for username, user_data in self.users_db.items():
            if (username == identifier or 
                user_data.get("email") == identifier or 
                user_data.get("phone") == identifier):
                
                if user_data.get("password") == password:  # Simple password check
                    found_user = user_data
                    found_user["username"] = username  # Add username to data
                    break
        
        if found_user:
            self._play_sound("success")
            self.current_user = found_user
            # Reset login attempts
            self.login_attempts = 3
            self.login_lockout = False
            self.show_user_dashboard()
        else:
            # Decrement attempts
            self.login_attempts -= 1
            self.attempts_label.configure(text=f"Attempts remaining: {self.login_attempts}")
            
            if self.login_attempts <= 0:
                self.handle_failed_login_attempts()
            else:
                self._animate_label(self.status_label, f"❌ Invalid credentials. {self.login_attempts} attempts remaining.", self.colors["danger"])
                self._play_sound("error")
                
    def handle_failed_login_attempts(self):
        """Handle failed login attempts with lockout periods"""
        self.login_lockout = True
        
        # Determine lockout duration based on previous lockouts
        lockout_seconds = 30  # First lockout: 30 seconds
        
        if hasattr(self, 'lockout_count'):
            if self.lockout_count == 1:
                lockout_seconds = 60  # Second lockout: 1 minute
            elif self.lockout_count == 2:
                lockout_seconds = 300  # Third lockout: 5 minutes
            else:
                lockout_seconds = 600  # Subsequent lockouts: 10 minutes
            self.lockout_count += 1
        else:
            self.lockout_count = 1
            
        # Display lockout message and start countdown
        self._animate_label(self.status_label, "⚠️ Too many failed attempts. Account locked.", self.colors["danger"])
        self._play_sound("error")
        
        # Start countdown timer
        self.start_lockout_timer(lockout_seconds)
        
    def start_lockout_timer(self, seconds):
        """Start a countdown timer for account lockout"""
        def update_timer(remaining):
            if remaining <= 0:
                self.timer_label.configure(text="")
                self.login_lockout = False
                self.login_attempts = 3
                self.attempts_label.configure(text=f"Attempts remaining: {self.login_attempts}")
                self.voice_attempts_label.configure(text=f"Attempts remaining: {self.login_attempts}")
                self._animate_label(self.status_label, "✅ You can try again now", self.colors["success"])
                return
                
            minutes = remaining // 60
            secs = remaining % 60
            self.timer_label.configure(text=f"Try again in {minutes:02d}:{secs:02d}")
            
            # Schedule next update
            self.lockout_timer = self.root.after(1000, lambda: update_timer(remaining - 1))
            
        # Clear any existing timer
        if self.lockout_timer:
            self.root.after_cancel(self.lockout_timer)
            
        # Start the timer
        update_timer(seconds)
        
    def authenticate_with_voice(self):
        """Authenticate using voice recognition"""
        if self.login_lockout:
            self._play_sound("error")
            return
            
        identifier = self.voice_login_entry.get()
        
        # Validate input
        if not identifier:
            self._animate_label(self.voice_status_label, "⚠️ Please enter your identifier", self.colors["danger"])
            self._play_sound("error")
            return
            
        # Check if the user exists
        found_user = None
        for username, user_data in self.users_db.items():
            if (username == identifier or 
                user_data.get("email") == identifier or 
                user_data.get("phone") == identifier):
                found_user = user_data
                found_user["username"] = username
                break
                
        if not found_user:
            # Provide hints
            hint_message = "❌ User not found. Try with registered username/email/phone"
            if "@" in identifier:
                hint_message = "❌ Email not found. Check for typos or register first"
            elif identifier.isdigit() or identifier.startswith("+"):
                hint_message = "❌ Phone number not found. Check for typos or register first"
            else:
                hint_message = "❌ Username not found. Check for typos or register first"
                
            self._animate_label(self.voice_status_label, hint_message, self.colors["danger"])
            self._play_sound("error")
            return
            
        # Make sure user has voice samples
        has_voice_samples = False
        if "voice_samples" in found_user and found_user["voice_samples"]:
            has_voice_samples = True
        
        # Simulate voice authentication with a dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Voice Authentication")
        dialog.geometry("400x300")  # Make the window slightly larger to add attempt count
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ctk.CTkLabel(
            dialog,
            text="Voice Authentication",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["primary"]
        ).pack(pady=(20, 10))
        
        instruction_label = ctk.CTkLabel(
            dialog,
            text="Please say: 'My voice is my password'",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        )
        instruction_label.pack(pady=5)
        
        # Add information if user has no voice samples
        if not has_voice_samples:
            warning_label = ctk.CTkLabel(
                dialog,
                text="Note: No voice samples found. Any voice will be accepted.",
                font=("Helvetica", 12, "italic"),
                text_color=self.colors["warning"]
            )
            warning_label.pack(pady=(0, 5))
        
        # Add display of remaining attempts in verification window
        attempts_label = ctk.CTkLabel(
            dialog,
            text=f"Attempts remaining: {self.login_attempts}",
            font=("Helvetica", 12),
            text_color=self.colors["text_alt"]
        )
        attempts_label.pack(pady=(0, 5))
        
        # Progress bar
        progress = ctk.CTkProgressBar(dialog, width=300)
        progress.pack(pady=10)
        progress.set(0)
        
        # Status label
        status_label = ctk.CTkLabel(
            dialog,
            text="Click 'Start Recording' when ready...",
            font=("Helvetica", 14),
            text_color=self.colors["text"]
        )
        status_label.pack(pady=5)
        
        # Recording state
        recording_active = [False]
        recording_completed = [False]  # To track recording completion
        authentication_result = [None]  # To store authentication result
        
        # Prepare path to save user's temporary verification recording
        verification_filename = os.path.join(
            self.voice_samples_dir, 
            f"verify_{found_user['username']}_{int(time.time())}.wav"
        )
        
        # Start recording button and continue to login
        def start_recording():
            if recording_completed[0]:
                # If recording is already completed and result is successful
                if authentication_result[0]:
                    # Continue to login
                    dialog.destroy()
                    self.current_user = found_user
                    self.show_user_dashboard()
                return
                
            recording_active[0] = True
            start_btn.configure(state="disabled")
            cancel_btn.configure(state="disabled")
            self._play_sound("click")
            
            status_label.configure(text="Recording... Please speak now.")
            
            # Simulate recording and processing
            def update_progress(value):
                if not recording_active[0]:
                    return
                    
                progress.set(value)
                if value < 1.0:
                    dialog.after(300, lambda: update_progress(value + 0.1))
                else:
                    recording_active[0] = False
                    recording_completed[0] = True
                    
                    # In a real application, we would record the voice and compare it with stored samples
                    # For testing, we simulate saving an audio file
                    with open(verification_filename, 'wb') as f:
                        f.write(b'DUMMY_VERIFICATION_SAMPLE')  # Dummy data for testing
                    
                    # In a real application, we would compare the recorded voice with stored samples
                    # If the user has voice samples, we verify them
                    # Otherwise we accept any voice (for testing only)
                    success = True
                    if has_voice_samples:
                        # Simulate comparison (in a real app there would be actual comparison)
                        # 90% chance of success, 10% chance of failure (for testing only)
                        import random
                        success = random.random() < 0.9
                    
                    authentication_result[0] = success
                    
                    if success:
                        # Successful verification
                        status_label.configure(text="✅ Voice authenticated successfully!")
                        self._play_sound("success")
                        
                        # Change record button to login button
                        start_btn.configure(
                            text="Login Now",
                            state="normal",
                            fg_color=self.colors["success"]
                        )
                    else:
                        # Failed verification
                        status_label.configure(text="❌ Voice authentication failed")
                        self._play_sound("error")
                        
                        # Reduce attempt count and update display
                        self.login_attempts -= 1
                        attempts_label.configure(text=f"Attempts remaining: {self.login_attempts}")
                        
                        # Enable retry if attempts remain
                        if self.login_attempts > 0:
                            start_btn.configure(text="Try Again", state="normal")
                        else:
                            # If attempts are exhausted, close window and show lockout message
                            dialog.after(1500, dialog.destroy)
                            dialog.after(1600, self.handle_failed_login_attempts)
            
            # Start progress
            update_progress(0)
        
        def cancel_recording():
            recording_active[0] = False
            # Try to delete temporary verification file if created
            try:
                if os.path.exists(verification_filename):
                    os.remove(verification_filename)
            except:
                pass
            dialog.destroy()
        
        # Buttons
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        start_btn = ctk.CTkButton(
            buttons_frame,
            text="Start Recording",
            command=start_recording,
            width=140,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            corner_radius=8
        )
        start_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=cancel_recording,
            width=100,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors["background"],
            hover_color=self.colors["secondary"],
            border_width=1,
            border_color=self.colors["primary"],
            text_color=self.colors["text"],
            corner_radius=8
        )
        cancel_btn.pack(side="left", padx=10)
    
    def handle_successful_login(self, user_data):
        """Handle successful login"""
        self.current_user = user_data
        # Reset login attempts
        self.login_attempts = 3
        self.login_lockout = False
        self.show_user_dashboard()
    
    def sign_out(self):
        """Sign out the current user"""
        self.current_user = None
        
        # Play sign out sound
        self._play_sound("click")
        
        # Hide current window
        if self.current_window:
            self.current_window.pack_forget()
            
        # Show login screen
        self.show_login_screen()
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

    def _hide_main_window(self):
        """Hide the main window"""
        if self.current_window:
            self.current_window.pack_forget()
    
    def _show_main_window(self):
        """Show the main window"""
        if self.current_window:
            self.current_window.pack_forget()
        self.show_login_screen()
        self.current_window = None

    def on_closing(self):
        """Handle window close event"""
        # Save user data before exiting the program
        try:
            self.save_user_data()
            print("User data saved successfully before exit.")
        except Exception as e:
            print(f"Error saving data before exit: {e}")
        
        # Add any cleanup operations here
        print("Closing application...")
        
        # Stop all threads
        for thread in threading.enumerate():
            if thread != threading.main_thread():
                print(f"Stopping thread: {thread.name}")
                # Cannot directly stop threads in Python, but we can set flags
                # that threads can check to see if they should stop
        
        # Destroy the window
        self.root.destroy()
        
        # For extra safety, exit the application
        os._exit(0)

# Create and run the application
if __name__ == "__main__":
    try:
        # Check if main.py exists
        if not os.path.exists("main.py"):
            print("Error: main.py file not found!")
            print("Creating a minimal main.py file...")
            
            # Create a minimal main.py file
            with open("main.py", "w") as f:
                f.write("""# Minimal BankVaultSystem implementation
class BankVaultSystem:
    def __init__(self):
        self.passwords = {}
        self.recorder = AudioRecorder()
        self.processor = AudioProcessor()
        self.verifier = SpeakerVerifier()
        
    def verify_password(self, identifier, password):
        # Simple mock implementation
        return True
        
    def verify_voice(self, identifier):
        # Simple mock implementation
        return True
        
    def check_user_exists(self, username, email, phone):
        # Simple mock implementation
        return False
        
    def create_user(self, full_name, username, email, phone, password, vault_details):
        # Simple mock implementation
        pass
        
    def delete_user(self, username):
        # Simple mock implementation
        pass

class AudioRecorder:
    def record_audio(self):
        print("Recording for 3 seconds...")
        time.sleep(1)
        print("Recording complete!")
        
    def save_recording(self, filename):
        print(f"Recording saved to {filename}")
        return filename

class AudioProcessor:
    def process_enrollment_samples(self, recordings):
        return []
        
    def process_verification_sample(self, recording):
        return []

class SpeakerVerifier:
    def train_model(self, user_id, features):
        pass
        
    def verify_speaker(self, user_id, features):
        return True, 0.95
        
    def list_users(self):
        return []
""")
            print("Minimal main.py file created.")
        
        app = BankVaultGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")