
"""
Tab for configuring Facebook login and application settings.
"""
import customtkinter as ctk
from tkinter import messagebox

class ConfigTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=0, pady=0)
        self._load_saved_login()
        self.build_config_tab()

    def _load_saved_login(self):
        try:
            from cryptography.fernet import Fernet
            import json
            import base64
            import os
            key_path = "facebooklogininfo.key"
            info_path = "facebooklogininfo.txt"
            if not (os.path.exists(key_path) and os.path.exists(info_path)):
                return
            with open(key_path, "rb") as kf:
                key = kf.read()
            fernet = Fernet(key)
            with open(info_path, "rb") as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted)
            data = json.loads(decrypted.decode("utf-8"))
            self.app._saved_email = data.get("email", "")
            self.app._saved_password = data.get("password", "")
            self.app._remember_me_checked = True
        except Exception:
            self.app._saved_email = ""
            self.app._saved_password = ""
            self.app._remember_me_checked = False

    def build_config_tab(self):
        frame = self.frame
        # Card-like container for login
        card = ctk.CTkFrame(frame, fg_color="#18223a", corner_radius=18)
        card.pack(pady=0, padx=0, ipadx=0, ipady=0, fill="both", expand=True)

        # Facebook icon (emoji fallback)
        icon = ctk.CTkLabel(card, text="\U0001F5E8", font=ctk.CTkFont(size=38))
        icon.pack(pady=(18, 6))

        # Modern header
        header = ctk.CTkLabel(card, text="Sign in to Facebook", font=ctk.CTkFont(size=22, weight="bold"), text_color="#b8c7e0")
        header.pack(pady=(0, 18))

        # Email
        email_label = ctk.CTkLabel(card, text="Email", font=ctk.CTkFont(size=14), text_color="#b8c7e0")
        email_label.pack(anchor="w", padx=18, pady=(0, 2))
        self.app.email_entry = ctk.CTkEntry(card, width=320, height=36, font=ctk.CTkFont(size=14), fg_color="#232b3e", border_color="#274472", text_color="#b8c7e0")
        self.app.email_entry.pack(padx=18, pady=(0, 12))
        # Autofill email if saved
        if hasattr(self.app, "_saved_email"):
            self.app.email_entry.insert(0, self.app._saved_email)

        # Password
        password_label = ctk.CTkLabel(card, text="Password", font=ctk.CTkFont(size=14), text_color="#b8c7e0")
        password_label.pack(anchor="w", padx=18, pady=(0, 2))
        self.app.password_entry = ctk.CTkEntry(card, width=320, height=36, show="*", font=ctk.CTkFont(size=14), fg_color="#232b3e", border_color="#274472", text_color="#b8c7e0")
        self.app.password_entry.pack(padx=18, pady=(0, 18))
        # Autofill password if saved
        if hasattr(self.app, "_saved_password"):
            self.app.password_entry.insert(0, self.app._saved_password)

        # Remember Me checkbox
        self.app.remember_me_var = ctk.BooleanVar()
        # Set checkbox if info was loaded
        if hasattr(self.app, "_remember_me_checked") and self.app._remember_me_checked:
            self.app.remember_me_var.set(True)
        remember_me_checkbox = ctk.CTkCheckBox(card, text="Remember Me", variable=self.app.remember_me_var, text_color="#b8c7e0", font=ctk.CTkFont(size=13))
        remember_me_checkbox.pack(anchor="w", padx=18, pady=(0, 12))

        # Login button
        login_btn = ctk.CTkButton(card, text="Login", command=self._login_with_remember, font=ctk.CTkFont(size=15, weight="bold"), fg_color="#1e2a47", hover_color="#274472", text_color="#b8c7e0", height=38, corner_radius=10)
        login_btn.pack(pady=(0, 12), padx=18, fill="x")

        # Status label
        self.app.config_status_label = ctk.CTkLabel(card, text="Not logged in", text_color="#7a869a", font=ctk.CTkFont(size=13))
        self.app.config_status_label.pack(pady=(0, 10))

    def _login_with_remember(self):
        email = self.app.email_entry.get()
        password = self.app.password_entry.get()
        remember = self.app.remember_me_var.get()
        # Call the original login method
        self.app.test_login()
        # Save login info if Remember Me is checked
        if remember:
            try:
                from cryptography.fernet import Fernet
                import json
                import os
                key_path = "facebooklogininfo.key"
                info_path = "facebooklogininfo.txt"
                # Generate key if not exists
                if not os.path.exists(key_path):
                    key = Fernet.generate_key()
                    with open(key_path, "wb") as kf:
                        kf.write(key)
                else:
                    with open(key_path, "rb") as kf:
                        key = kf.read()
                fernet = Fernet(key)
                data = json.dumps({"email": email, "password": password}).encode("utf-8")
                encrypted = fernet.encrypt(data)
                with open(info_path, "wb") as f:
                    f.write(encrypted)
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save login info: {e}")
