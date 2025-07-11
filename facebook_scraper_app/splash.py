"""
Splash screen utility for Facebook Scraper.
"""

def show_splash_screen():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        splash = tk.Toplevel()
        splash.title("Facebook Scraper")
        width, height = 480, 200
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        splash.resizable(False, False)
        label = tk.Label(
            splash,
            text="Loading Facebook Scraper...\nPlease wait...",
            font=("Arial", 16),
            pady=40
        )
        label.pack(expand=True)
        splash.update()
        return root, splash
    except Exception:
        return None, None
