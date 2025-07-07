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
