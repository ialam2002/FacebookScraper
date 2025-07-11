
"""
Main entry point for the Facebook Scraper GUI application.
Initializes and runs the main application window.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # 2 = only errors, 3 = suppress all
from gui.gui import FacebookScraperApp

if __name__ == "__main__":
    app = None
    try:
        app = FacebookScraperApp()
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        if app is not None:
            app.destroy()
