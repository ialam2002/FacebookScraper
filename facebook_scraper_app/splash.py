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
        # Add logo above loading text
        try:
            from PIL import Image, ImageTk
            import os
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo", "gny-logo.png")
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((100, 100), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(splash, image=logo_photo)
            logo_label.image = logo_photo  # Keep reference
            logo_label.pack(pady=(20, 10))
        except Exception as e:
            print(f"Splash logo error: {e}")
        label = tk.Label(
            splash,
            text="Loading Claimant Connection Search (CCS)...\nPlease wait...",
            font=("Arial", 16),
            pady=20
        )
        label.pack(expand=True)
        splash.update()
        return root, splash
    except Exception:
        return None, None
