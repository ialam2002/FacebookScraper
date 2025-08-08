
"""
Facebook friends scraping logic using Selenium automation.
Handles login, navigation, and data extraction.
"""

# Standard library imports
import json
import os
import sys
import time
from collections import deque
from tkinter import messagebox

# Third-party imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacebookFriendsScraper:
    def __init__(self, driver_path=None, driver=None):
        """Initialize the scraper with bundled chromedriver or use existing driver."""
        self.driver_path = self._get_driver_path(driver_path) if driver is None else None
        self.driver = driver if driver is not None else self._initialize_driver()
        self.logged_in = False
        self.visited_profiles = set()

    def _get_driver_path(self, driver_path):
        """Determine the correct chromedriver path for packaged or dev environment."""
        if driver_path:
            return driver_path
            
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running in normal Python environment - go up from scraper/ to facebook_scraper_app/
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Look for chromedriver in the chromedriver subdirectory
        return os.path.join(base_path, 'chromedriver', 'chromedriver.exe')
    
    def _initialize_driver(self):
        """Initialize and configure the Chrome driver."""
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            return webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)
        except Exception as e:
            messagebox.showerror(
                "ChromeDriver Error",
                f"Failed to initialize ChromeDriver: {str(e)}\n\n"
                "Please ensure:\n"
                "1. Chrome browser is installed\n"
                "2. Your Chrome version matches the bundled ChromeDriver\n"
                "3. No other ChromeDriver instances are running"
            )
            raise
    
    def login(self, email, password):
        """Log in to Facebook."""
        print("Logging in to Facebook...")
        self.driver.get("https://www.facebook.com")
        
        try:
            # Accept cookies if the popup appears
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(string(), 'Allow essential and optional cookies')]"))
                )
                cookie_button.click()
            except:
                pass  # Cookie popup didn't appear
            
            email_elem = self.driver.find_element(By.ID, "email")
            email_elem.send_keys(email)
            time.sleep(2)
            password_elem = self.driver.find_element(By.ID, "pass")
            password_elem.send_keys(password)
            time.sleep(2)
            password_elem.send_keys(Keys.RETURN)
            time.sleep(5)  # Wait for login to complete
            
            # Verify login was successful
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Facebook')]"))
                )
                self.logged_in = True
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def _get_profile_name(self):
        """Extract the profile name from the current page."""
        try:
            print(f"Current URL: {self.driver.current_url}")
            print("Attempting to extract profile name...")
            
            # Wait for page to load completely
            time.sleep(3)
            
            # Try to find any h1 elements first to see what's available
            try:
                all_h1s = self.driver.find_elements(By.TAG_NAME, "h1")
                print(f"Found {len(all_h1s)} h1 elements on page")
                for i, h1 in enumerate(all_h1s[:3]):  # Check first 3 h1s
                    try:
                        text = h1.text.strip()
                        classes = h1.get_attribute("class")
                        print(f"H1 #{i+1}: text='{text}', classes='{classes}'")
                    except:
                        pass
            except Exception as e:
                print(f"Error checking h1 elements: {e}")
            
            # Try multiple selectors to find the profile name
            selectors = [
                '//span[@dir="auto"]/h1[contains(@class, "x1qlqyl8")]',
                '//h1[contains(@class, "x1qlqyl8") and contains(@class, "html-h1")]',
                '//h1[contains(@class, "x1qlqyl8")]',
                '//h1[contains(@class, "html-h1")]',
                '//*[contains(@class, "x1qlqyl8")]',
                '//h1'  # Last resort - any h1
            ]
            
            name_element = None
            for i, selector in enumerate(selectors):
                try:
                    print(f"Trying selector {i+1}: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                    print(f"Found {len(elements)} elements for selector {i+1}")
                    
                    if elements:
                        # Try each element until we find one with non-empty text
                        for j, element in enumerate(elements):
                            try:
                                text = element.text.strip()
                                print(f"Element {j+1} text: '{text}'")
                                if text and text != "Notifications" and len(text) > 1:
                                    name_element = element
                                    print(f"Using element {j+1} from selector {i+1} with text: '{text}'")
                                    break
                            except:
                                continue
                        
                        if name_element:
                            break
                            
                except Exception as e:
                    print(f"Selector {i+1} failed: {str(e)}")
                    continue
            
            if name_element is None:
                print("Could not find profile name element with any selector")
                # Try to get page source snippet for debugging
                try:
                    page_source = self.driver.page_source
                    if "Jose Sone" in page_source:
                        print("'Jose Sone' found in page source, but couldn't locate element")
                    else:
                        print("'Jose Sone' not found in page source")
                except:
                    pass
                return "Unknown"
            
            # Get text and clean up non-breaking spaces and extra whitespace
            try:
                raw_text = name_element.text
                print(f"Raw text from element: '{raw_text}'")
                print(f"Element tag: {name_element.tag_name}")
                print(f"Element classes: {name_element.get_attribute('class')}")
                
                if not raw_text:
                    # Try to get innerHTML if text is empty
                    inner_html = name_element.get_attribute('innerHTML')
                    print(f"Element innerHTML: '{inner_html}'")
                    # Extract text from HTML if needed
                    import re
                    text_match = re.search(r'>([^<]+)<', inner_html)
                    if text_match:
                        raw_text = text_match.group(1)
                        print(f"Extracted text from innerHTML: '{raw_text}'")
                
                profile_name = raw_text.replace('\u00a0', ' ').strip()
                # Remove any trailing spaces after cleaning
                profile_name = ' '.join(profile_name.split())
                print(f"Final extracted profile name: '{profile_name}'")
                return profile_name if profile_name else "Unknown"
                
            except Exception as e:
                print(f"Error extracting text from element: {e}")
                return "Unknown"
            
        except Exception as e:
            print(f"Could not extract profile name: {e}")
            import traceback
            traceback.print_exc()
            return "Unknown"
    
    def get_friends_list(self, profile_url, max_friends=2000):
        """
        Get the friends list for a given profile URL using infinite scrolling.
        Returns a dictionary with profile info and friends list including profile pictures.
        """
        if not self.logged_in:
            print("Please login first")
            return None
            
        result = {
            'profile_name': '',
            'profile_url': profile_url,
            'profile_pic': None,  # Add this field for the profile's picture
            'friends': []
        }
        
        try:
            # Go to profile and get name
            self.driver.get(profile_url)
            time.sleep(3)
            profile_name = self._get_profile_name()
            result['profile_name'] = profile_name
            
            # Get the profile picture of the user whose friends we're scraping
            try:
                # Try to find the profile picture container
                parent_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, 
                        "//div[contains(@class, 'x1jx94hy') and " +
                        "contains(@class, 'x1c9tyrk') and " +
                        "contains(@class, 'xeusxvb')]"))
                )
                
                # Find the profile picture div inside it
                profile_pic_div = parent_container.find_element(
                    By.XPATH,
                    ".//div[contains(@class, 'x1rg5ohu') and " +
                    "contains(@class, 'x1n2onr6') and " +
                    "contains(@class, 'x3ajldb') and " +
                    "contains(@class, 'x1ja2u2z')]"
                )
                
                # Extract the SVG > image URL
                svg = profile_pic_div.find_element(By.TAG_NAME, "svg")
                image = svg.find_element(By.TAG_NAME, "image")
                profile_pic_url = image.get_attribute("xlink:href") or image.get_attribute("href")
                
                if profile_pic_url:
                    result['profile_pic'] = profile_pic_url
                    print(f"Found profile picture for {profile_name}: {profile_pic_url}")
            except Exception as e:
                print(f"Could not extract profile picture for {profile_name}: {e}")
            
            # Navigate to friends page
            try:
                # Try clicking the Friends link
                friends_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, 'Friends')))
                friends_link.click()
                time.sleep(3)
            except:
                # Fallback to direct friends URL
                self.driver.get(profile_url + "/friends")
                time.sleep(3)
                
            # Infinite scroll implementation
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            no_new_friends_count = 0
            max_no_new_friends = 20  # Allow even more scrolls before stopping
            min_scrolls = 10  # Require at least this many scrolls before allowing early stop
            scrolls_done = 0

            # XPath for the friends container
            friends_container_xpath = "//div[contains(@class, 'x78zum5') and contains(@class, 'x1q0g3np') and contains(@class, 'x1a02dak') and contains(@class, 'x1qughib')]"
            friend_link_xpath = ".//a[contains(@href, '/') and .//span[@dir='auto']]"


            while True:
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.7)
                scrolls_done += 1

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_new_friends_count += 1
                else:
                    no_new_friends_count = 0

                last_height = new_height

                # Find friend elements only within the friends container
                try:
                    friends_container = self.driver.find_element(By.XPATH, friends_container_xpath)
                    friend_elements = friends_container.find_elements(By.XPATH, friend_link_xpath)
                except Exception:
                    friend_elements = []

                print(f"Scroll: {scrolls_done} | No new: {no_new_friends_count}/{max_no_new_friends} | Friends found: {len(friend_elements)}")

                # Only allow early stop after min_scrolls
                if len(friend_elements) >= max_friends or (scrolls_done >= min_scrolls and no_new_friends_count >= max_no_new_friends):
                    print("Stopping scroll: either max friends reached or no new friends loaded after several scrolls.")
                    break

            # Find all friend link elements within the friends container
            try:
                friends_container = self.driver.find_element(By.XPATH, friends_container_xpath)
                friend_elements = friends_container.find_elements(By.XPATH, friend_link_xpath)
            except Exception:
                friend_elements = []
            
            # Find all profile picture elements
            profile_pics = self.driver.find_elements(By.XPATH, '//div[contains(@class, "x6s0dn4")]//img[contains(@class, "x1obq294")]')
            
            # Create a list of profile picture URLs
            profile_pic_urls = [img.get_attribute('src') for img in profile_pics if img.get_attribute('src')]
            
            seen_urls = set()
            for i, element in enumerate(friend_elements):
                if len(result['friends']) >= max_friends:
                    break
                    
                try:
                    href = element.get_attribute('href')
                    name = element.find_element(By.XPATH, './/span[@dir="auto"]').text
                    
                    # Skip if this is the profile owner or a duplicate
                    if (href and name and href not in seen_urls and 
                        "facebook.com" in href and 
                        name != profile_name and  # Skip if name matches profile owner
                        href != profile_url):     # Skip if URL matches profile URL
                        
                        # Get profile picture URL if available
                        profile_pic = profile_pic_urls[i] if i < len(profile_pic_urls) else None
                        
                        result['friends'].append({
                            'name': name,
                            'url': href,
                            'profile_pic': profile_pic  # Add profile picture URL
                        })
                        seen_urls.add(href)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error getting friends for {profile_url}: {e}")
        
        return result
    
    def scrape_friends_network(self, start_urls, depth=0, max_friends_per_profile=100, output_file=None):
        """
        Scrape friends network up to a specified depth using BFS approach.
        """
        if not self.logged_in:
            print("Please login first")
            return None
            
        network = {}
        queue = deque()
        
        # Initialize queue with starting profiles
        for url in start_urls:
            if url not in self.visited_profiles:
                queue.append((url, 0))  # (url, current_depth)
                self.visited_profiles.add(url)
        
        while queue:
            current_url, current_depth = queue.popleft()
            
            # Skip if we've reached max depth
            if current_depth > depth:
                continue
                
            print(f"\nProcessing profile (depth {current_depth}): {current_url}")
            
            # Get friends for current profile
            friends_data = self.get_friends_list(current_url, max_friends=max_friends_per_profile)
            
            if not friends_data:
                continue
                
            # Add to network structure
            if current_url not in network:
                network[current_url] = {
                    'profile_name': friends_data['profile_name'],
                    'profile_pic': friends_data.get('profile_pic'),  # Store profile picture
                    'depth': current_depth,
                    'friends': []
                }
            
            # Process friends - including profile pictures
            for friend in friends_data['friends']:
                network[current_url]['friends'].append({
                    'name': friend['name'],
                    'url': friend['url'],
                    'profile_pic': friend.get('profile_pic')  # Include profile picture URL
                })
                
                # Add to queue for next level if we haven't reached max depth
                if current_depth < depth and friend['url'] not in self.visited_profiles:
                    queue.append((friend['url'], current_depth + 1))
                    self.visited_profiles.add(friend['url'])
            
            # Save intermediate results
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(network, f, ensure_ascii=False, indent=2)
            
            #delay
            time.sleep(0.5)
        
        return network
    
    def close(self):
        """Close the browser (only if we own the driver)."""
        if hasattr(self, 'driver') and self.driver and self.driver_path is not None:
            self.driver.quit()