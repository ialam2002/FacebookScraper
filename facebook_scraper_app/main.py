
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


if __name__ == "__main__":
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
        # Wait for pre-import to finish or timeout (max 2 seconds for UI responsiveness)
        preimport_done.wait(timeout=2)
        from gui.gui import FacebookScraperApp
        if splash:
            splash.destroy()
        if splash_root:
            splash_root.destroy()
        app = FacebookScraperApp()
        app.mainloop()
    except Exception as e:
        if splash:
            splash.destroy()
        if splash_root:
            splash_root.destroy()
        print(f"Application error: {e}")
        if app is not None:
            app.destroy()
