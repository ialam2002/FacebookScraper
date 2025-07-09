
"""
Tab for configuring Facebook login and application settings.
"""
import customtkinter as ctk
from tkinter import messagebox

class ConfigTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_config_tab()

    def build_config_tab(self):
        frame = self.frame
        header = ctk.CTkLabel(frame, text="Facebook Login", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(pady=(0, 15))

        email_label = ctk.CTkLabel(frame, text="Facebook Email:")
        email_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.app.email_entry = ctk.CTkEntry(frame, width=400)
        self.app.email_entry.pack(padx=10, pady=(0, 10))

        password_label = ctk.CTkLabel(frame, text="Facebook Password:")
        password_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.app.password_entry = ctk.CTkEntry(frame, width=400, show="*")
        self.app.password_entry.pack(padx=10, pady=(0, 15))

        login_btn = ctk.CTkButton(frame, text="Login", command=self.app.test_login)
        login_btn.pack(pady=10)

        self.app.config_status_label = ctk.CTkLabel(frame, text="Not logged in", text_color="gray")
        self.app.config_status_label.pack(pady=5)
