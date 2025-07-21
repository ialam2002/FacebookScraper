
"""
Main entry point for the Facebook Scraper GUI application.
Initializes and runs the main application window.
"""


import os

import threading
# Suppress TensorFlow warnings early
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # 2 = only errors, 3 = suppress all

# Import splash screen from separate module
from splash import show_splash_screen



import sys
import tkinter.messagebox as messagebox

def check_dependencies():
    chromedriver_path = os.path.join(os.path.dirname(__file__), 'chromedriver', 'chromedriver.exe')
    if not os.path.isfile(chromedriver_path):
        messagebox.showerror("Dependency Error", f"chromedriver.exe not found at {chromedriver_path}. Please ensure it is present.")
        return False
    return True

def cleanup_splash(splash, splash_root):
    try:
        if splash:
            splash.destroy()
    except Exception:
        pass
    try:
        if splash_root:
            splash_root.destroy()
    except Exception:
        pass

def startup():
    app = None
    splash_root, splash = show_splash_screen()

    # Pre-import heavy modules in a background thread while splash is shown
    preimport_done = threading.Event()
    def preimport_heavy():
        try:
            import gui.gui
            import profile_search.search
            import gui.visualization
        except Exception:
            pass
        preimport_done.set()

    preimport_thread = threading.Thread(target=preimport_heavy, daemon=True)
    preimport_thread.start()

    try:
        # Dependency check before proceeding
        if not check_dependencies():
            cleanup_splash(splash, splash_root)
            sys.exit(1)

        # Wait for pre-import to finish or timeout (max 2 seconds for UI responsiveness)
        preimport_done.wait(timeout=2)
        from gui.gui import FacebookScraperApp
        cleanup_splash(splash, splash_root)
        app = FacebookScraperApp()
        app.mainloop()
    except Exception as e:
        cleanup_splash(splash, splash_root)
        print(f"Application error: {e}")
        if app is not None:
            try:
                app.destroy()
            except Exception:
                pass

if __name__ == "__main__":
    startup()
