
"""
Controller for managing Facebook scraping logic and driver lifecycle.
"""
from scraper.scraper import FacebookFriendsScraper

class ScraperController:
    def __init__(self):
        self.scraper = None
        self.logged_in = False
        self.driver = None  # Store the driver instance

    def login(self, email, password):
        try:
            # Only create driver if not already created
            if self.driver is None:
                self.scraper = FacebookFriendsScraper(driver_path=r"C:\Users\nuixalam\Desktop\FacebookScraper\facebook_scraper_app\chromedriver\chromedriver.exe")
                self.driver = self.scraper.driver
            else:
                self.scraper = FacebookFriendsScraper(driver_path=None)
                self.scraper.driver = self.driver
            self.logged_in = self.scraper.login(email, password)
            if not self.logged_in:
                # If login failed, close and reset driver so user can try again
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass
                    self.driver = None
                self.scraper = None
            return self.logged_in
        except Exception as e:
            # On any error, also reset driver and scraper
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
            self.scraper = None
            raise Exception(f"Login failed: {str(e)}")

    def get_driver(self):
        return self.driver

    def scrape_friends_network(self, start_urls, depth, max_friends_per_profile, output_file):
        # Always re-initialize the scraper for each run, but reuse the persistent driver
        if self.driver is None or not self.logged_in:
            raise Exception("Scraper not initialized or not logged in")
        self.scraper = FacebookFriendsScraper(driver_path=None, driver=self.driver)
        self.scraper.logged_in = True
        return self.scraper.scrape_friends_network(
            start_urls=start_urls,
            depth=depth,
            max_friends_per_profile=max_friends_per_profile,
            output_file=output_file
        )

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logged_in = False