
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
        self.build_config_tab()

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

        # Password
        password_label = ctk.CTkLabel(card, text="Password", font=ctk.CTkFont(size=14), text_color="#b8c7e0")
        password_label.pack(anchor="w", padx=18, pady=(0, 2))
        self.app.password_entry = ctk.CTkEntry(card, width=320, height=36, show="*", font=ctk.CTkFont(size=14), fg_color="#232b3e", border_color="#274472", text_color="#b8c7e0")
        self.app.password_entry.pack(padx=18, pady=(0, 18))

        # Login button
        login_btn = ctk.CTkButton(card, text="Login", command=self.app.test_login, font=ctk.CTkFont(size=15, weight="bold"), fg_color="#1e2a47", hover_color="#274472", text_color="#b8c7e0", height=38, corner_radius=10)
        login_btn.pack(pady=(0, 12), padx=18, fill="x")

        # Status label
        self.app.config_status_label = ctk.CTkLabel(card, text="Not logged in", text_color="#7a869a", font=ctk.CTkFont(size=13))
        self.app.config_status_label.pack(pady=(0, 10))
