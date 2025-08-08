"""
Facebook posts scraping logic using Selenium automation.
Handles navigation and post extraction from user profiles.
"""

# Standard library imports
import json
import os
import re
import time

# Third-party imports
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacebookPostsScraper:
    @staticmethod
    def normalize_facebook_profile_url(url):
        """Normalize Facebook profile URLs to remove all query parameters, fragments, and trailing slashes."""
        if not url:
            return url
        # Remove everything after '?' (query params)
        url = url.split('?', 1)[0]
        # Remove everything after '#' (fragment)
        url = url.split('#', 1)[0]
        # Remove trailing slash if present
        if url.endswith('/'):
            url = url[:-1]
        return url
        
    def __init__(self, driver):
        """Initialize the scraper with an existing driver instance."""
        self.driver = driver
        self.visited_profiles = set()

    def _get_profile_name(self):
        """Extract the profile name from the current page."""
        try:
            print(f"Current URL: {self.driver.current_url}")
            print("Attempting to extract profile name...")
            
            # Wait for page to load completely
            time.sleep(3)
            
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
                    elements = self.driver.find_elements(By.XPATH, selector)
                    
                    if elements:
                        # Try each element until we find one with non-empty text
                        for element in elements:
                            try:
                                text = element.text.strip()
                                if text and text != "Notifications" and len(text) > 1:
                                    name_element = element
                                    break
                            except:
                                continue
                        
                        if name_element:
                            break
                            
                except Exception as e:
                    continue
            
            if name_element is None:
                return "Unknown"
            
            # Get text and clean up
            try:
                raw_text = name_element.text
                profile_name = raw_text.replace('\u00a0', ' ').strip()
                profile_name = ' '.join(profile_name.split())
                return profile_name if profile_name else "Unknown"
                
            except Exception as e:
                return "Unknown"
                
        except Exception as e:
            print(f"Error extracting profile name: {e}")
            return "Unknown"

    def scrape_posts(self, profile_url, max_posts=1000000):
        """Scrape people who liked posts from a Facebook profile."""
        print(f"Scraping post likes from: {profile_url}")
        
        result = {
            'profile_url': profile_url,
            'profile_name': 'Unknown',
            'post_likes': []  # Changed from 'posts' to 'post_likes'
        }
        
        try:
            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(3)

            # Ensure we are on the Posts tab

            try:
                # Wait for the Posts tab <a> element to appear (role='tab', contains span with text 'Posts')
                posts_tab_xpath = "//a[@role='tab' and .//span[contains(text(), 'Posts') and contains(@class, 'x193iq5w')]]"
                posts_tab_a = WebDriverWait(self.driver, 7).until(
                    lambda d: d.find_element(By.XPATH, posts_tab_xpath)
                )
                print("Found Posts tab <a> element.")
                from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException
                for attempt in range(3):
                    try:
                        posts_tab_a = self.driver.find_element(By.XPATH, posts_tab_xpath)
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", posts_tab_a)
                        WebDriverWait(self.driver, 2).until(lambda d: posts_tab_a.is_displayed() and posts_tab_a.is_enabled())
                        time.sleep(0.5)
                        try:
                            posts_tab_a.click()
                        except ElementNotInteractableException:
                            print("Element not interactable, trying JavaScript click...")
                            self.driver.execute_script("arguments[0].click();", posts_tab_a)
                        print("Clicked Posts tab (<a> method).")
                        time.sleep(2)
                        break
                    except (StaleElementReferenceException, ElementNotInteractableException) as ex:
                        print(f"Exception on attempt {attempt+1}: {ex}, retrying...")
                        time.sleep(1)
                else:
                    print("Failed to click Posts tab after retries due to stale or not interactable element.")
            except Exception as e:
                print(f"Could not robustly find or click Posts tab: {e}")

            # Get profile name
            result['profile_name'] = self._get_profile_name()
            print(f"Profile name: {result['profile_name']}")

            # Extract likes from multiple posts
            print("Looking for posts with likes...")
            post_likes = self._extract_multiple_post_likes(max_posts)
            result['post_likes'] = post_likes

            print(f"Successfully scraped likes from {len(post_likes)} posts")

        except Exception as e:
            print(f"Error scraping post likes for {profile_url}: {e}")

        return result

    def _extract_multiple_post_likes(self, max_posts):
        """Find and process multiple posts with likes. Scrolls until no more new posts can be loaded."""
        all_post_likes = []
        processed_elements = set()  # Track elements we've already clicked
        try:
            posts_processed = 0
            scroll_position = 0
            no_new_posts_scrolls = 0
            max_no_new_posts_scrolls = 10  # Stop after 10 scrolls with no new posts found
            last_total_elements = 0
            # Find all post containers
            post_container_xpath = "//div[contains(@class, 'x1yztbdb') and contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3') and contains(@class, 'x1ja2u2z')]"
            processed_like_imgs = set()
            last_post_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 15
            next_container_idx = 0
            while posts_processed < max_posts:
                post_containers = self.driver.find_elements(By.XPATH, post_container_xpath)
                print(f"Found {len(post_containers)} post containers.")
                new_posts_found = False
                # Find the next unprocessed post container in order
                found_next = False
                for idx in range(next_container_idx, len(post_containers)):
                    post_div = post_containers[idx]
                    like_img_elems = post_div.find_elements(By.XPATH, './/img[contains(@class, "x16dsc37") and @height="18" and @width="18" and @role="presentation"]')
                    if not like_img_elems:
                        continue
                    img_elem = like_img_elems[0]
                    img_loc = tuple(img_elem.location.items())
                    if img_loc in processed_like_imgs:
                        continue
                    print(f"\n=== Processing post {posts_processed + 1} (container {idx+1}) ===")
                    print(f"Clicking like button at location {img_elem.location}...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img_elem)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", img_elem)
                    time.sleep(3)
                    processed_like_imgs.add(img_loc)
                    new_posts_found = True
                    found_next = True
                    next_container_idx = idx + 1
                    # Verify popup opened
                    popups = self.driver.find_elements(By.XPATH, '//div[@role="dialog" or contains(@aria-label, "People who reacted")]')
                    if not popups:
                        print("✗ No popup appeared after clicking <img> element")
                        break
                    print("✓ Successfully opened likes popup by clicking <img> element!")
                    # Extract likes from popup with scrolling
                    print("Extracting likes from popup...")
                    liked_by = self._extract_likes_from_popup_with_scroll()
                    post_data = {
                        'post_number': posts_processed + 1,
                        'likes_count': '',  # likes count not available from img, can be improved
                        'liked_by': liked_by
                    }
                    all_post_likes.append(post_data)
                    posts_processed += 1
                    print(f"✓ Successfully processed post {posts_processed} with {len(liked_by)} likes")
                    # Close popup by clicking elsewhere
                    self._close_popup_by_clicking_elsewhere()
                    # Scroll to the next unprocessed post container if available
                    if next_container_idx < len(post_containers):
                        next_post_div = post_containers[next_container_idx]
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_post_div)
                        time.sleep(1)
                    else:
                        # If no next post container, scroll further to load more
                        self.driver.execute_script("window.scrollBy(0, 1000);")
                        scroll_position += 1000
                        time.sleep(2)
                    break
                if not found_next:
                    # If no new posts found, scroll further to load more
                    scroll_attempts += 1
                    print(f"No new posts found, scrolling down to load more... (attempt {scroll_attempts}/{max_scroll_attempts})")
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                    scroll_position += 1000
                    time.sleep(3)
                    # If after several scrolls no new posts appear, stop
                    if len(post_containers) == last_post_count:
                        if scroll_attempts >= max_scroll_attempts:
                            print("No more new posts can be loaded. Stopping.")
                            break
                    else:
                        last_post_count = len(post_containers)
                        scroll_attempts = 0
                # If no new posts found, scroll further to load more
                if not new_posts_found:
                    scroll_attempts += 1
                    print(f"No new posts found, scrolling down to load more... (attempt {scroll_attempts}/{max_scroll_attempts})")
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                    scroll_position += 1000
                    time.sleep(3)
                    # If after several scrolls no new posts appear, stop
                    if len(post_containers) == last_post_count:
                        if scroll_attempts >= max_scroll_attempts:
                            print("No more new posts can be loaded. Stopping.")
                            break
                    else:
                        last_post_count = len(post_containers)
                        scroll_attempts = 0
            print(f"\n=== Completed processing {len(all_post_likes)} posts ===")
            return all_post_likes
            
        except Exception as e:
            print(f"Error processing multiple posts: {e}")
            return all_post_likes

    def _extract_likes_from_popup_with_scroll(self):
        """Extract names and profile URLs from the likes popup with scrolling."""
        liked_by = []
        try:
            # Wait for popup to fully load
            time.sleep(2)
            print("Scrolling likes popup using user elements as anchors...")

            last_count = 0
            no_change_count = 0
            max_no_change = 3  # Stop if no new users after this many scrolls
            scrolls = 0
            while no_change_count < max_no_change:
                user_elements = self.driver.find_elements(By.XPATH, "//div[@data-visualcompletion='ignore-dynamic' and contains(@style, 'padding-left: 8px; padding-right: 8px')]")
                current_users = len(user_elements)
                if user_elements:
                    anchor = user_elements[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", anchor)
                else:
                    print("No user elements found to scroll to.")
                    break
                time.sleep(0.7)
                print(f"Found {current_users} users after scroll {scrolls+1}")
                if current_users > last_count:
                    last_count = current_users
                    no_change_count = 0
                else:
                    no_change_count += 1
                scrolls += 1
            print(f"Finished scrolling. Total users found: {last_count}")

            # Now extract all the users
            liked_by = self._extract_users_from_popup()
            return liked_by
        except Exception as e:
            print(f"Error extracting likes from popup with scroll: {e}")
            return []

    def _count_users_in_popup(self):
        """Count the number of users currently visible in the popup."""
        try:
            user_containers = self.driver.find_elements(By.XPATH, '//div[@data-visualcompletion="ignore-dynamic" and contains(@style, "padding-left: 8px; padding-right: 8px")]')
            return len(user_containers)
        except:
            return 0

    def _extract_users_from_popup(self):
        """Extract user data from the popup."""
        liked_by = []
        seen_urls = set()
        
        try:
            # Based on your specific HTML structure
            user_containers = self.driver.find_elements(By.XPATH, '//div[@data-visualcompletion="ignore-dynamic" and contains(@style, "padding-left: 8px; padding-right: 8px")]')
            
            print(f"Found {len(user_containers)} user containers")
            
            for i, container in enumerate(user_containers):
                try:
                    # Look for name links within each container
                    name_links = container.find_elements(By.XPATH, './/a[contains(@class, "x1i10hfl") and contains(@href, "facebook.com") and not(contains(@href, "/friends")) and not(contains(@href, "/photos")) and not(contains(@href, "/videos")) and not(contains(@href, "/map"))]')
                    
                    for link in name_links:
                        try:
                            raw_url = link.get_attribute('href')
                            profile_url = self.normalize_facebook_profile_url(raw_url)
                            name = link.text.strip()
                            
                            if (profile_url and name and 
                                profile_url not in seen_urls and 
                                len(name) > 1 and
                                name not in ["Add friend", "Friends", "Photos", "Videos", "Check-ins"]):
                                
                                print(f"User {len(liked_by)+1}: {name} -> {profile_url[:50]}...")
                                
                                liked_by.append({
                                    'name': name,
                                    'profile_url': profile_url
                                })
                                
                                seen_urls.add(profile_url)
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
            
            # Fallback method if the above didn't work
            if len(liked_by) == 0:
                print("First approach found no users, trying fallback...")
                name_spans = self.driver.find_elements(By.XPATH, '//span[@class="xjp7ctv"]/a[contains(@href, "facebook.com") and not(contains(@href, "/friends")) and not(contains(@href, "/photos")) and not(contains(@href, "/videos")) and not(contains(@href, "/map"))]')
                
                for span_link in name_spans:
                    try:
                        profile_url = span_link.get_attribute('href')
                        name = span_link.text.strip()
                        
                        if (profile_url and name and 
                            profile_url not in seen_urls and 
                            len(name) > 1):
                            
                            liked_by.append({
                                'name': name,
                                'profile_url': profile_url
                            })
                            
                            seen_urls.add(profile_url)
                            
                    except Exception as e:
                        continue
            
            print(f"Successfully extracted {len(liked_by)} people who liked the post")
            return liked_by
            
        except Exception as e:
            print(f"Error extracting users from popup: {e}")
            return []

    def _close_popup_by_clicking_elsewhere(self):
        """Close the popup by clicking elsewhere on the screen."""
        try:
            print("Closing popup by clicking elsewhere...")
            
            # Method 1: Look for a close button first
            close_buttons = self.driver.find_elements(By.XPATH, '//div[@aria-label="Close" or @role="button"][contains(@style, "cursor: pointer")]')
            if close_buttons:
                print("Found close button, clicking it...")
                self.driver.execute_script("arguments[0].click();", close_buttons[0])
                time.sleep(2)
                print("Popup closed with close button")
                return
            
            # Method 2: Look for X button
            x_buttons = self.driver.find_elements(By.XPATH, '//div[text()="✕" or contains(@aria-label, "Close")]')
            if x_buttons:
                print("Found X button, clicking it...")
                self.driver.execute_script("arguments[0].click();", x_buttons[0])
                time.sleep(2)
                print("Popup closed with X button")
                return
            
            # Method 3: Click on backdrop/overlay
            overlays = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]/../div[1]')
            if overlays:
                print("Found overlay, clicking it...")
                self.driver.execute_script("arguments[0].click();", overlays[0])
                time.sleep(2)
                print("Popup closed with overlay click")
                return
            
            # Method 4: Click outside the dialog area
            try:
                # Find the dialog and click outside its bounds
                dialogs = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]')
                if dialogs:
                    # Get dialog position and click outside it
                    dialog = dialogs[0]
                    location = dialog.location
                    size = dialog.size
                    
                    # Click to the left of the dialog
                    click_x = max(10, location['x'] - 50)
                    click_y = location['y'] + (size['height'] // 2)
                    
                    print(f"Clicking outside dialog at position ({click_x}, {click_y})")
                    self.driver.execute_script(f"document.elementFromPoint({click_x}, {click_y}).click();")
                    time.sleep(2)
                    print("Popup closed by clicking outside dialog")
                    return
            except Exception as e:
                print(f"Error with outside click method: {e}")
            
            # Method 5: Press Escape key
            print("Trying Escape key...")
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(2)
            print("Popup closed with Escape key")
            
        except Exception as e:
            print(f"Error closing popup: {e}")
            # Final fallback: Force reload if nothing else works
            try:
                print("All methods failed, trying final fallback...")
                # Click on the main content area
                main_content = self.driver.find_elements(By.XPATH, '//div[@role="main"]')
                if main_content:
                    self.driver.execute_script("arguments[0].click();", main_content[0])
                    time.sleep(2)
                else:
                    # Last resort - click on body with different coordinates
                    self.driver.execute_script("document.elementFromPoint(100, 100).click();")
                    time.sleep(2)
                print("Popup closed with fallback method")
            except:
                print("Could not close popup with any method")

