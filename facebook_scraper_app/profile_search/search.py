
"""
Profile search and face matching logic for Facebook Scraper.
Includes image processing and Selenium automation.
"""
import requests
import cv2
import numpy as np
from deepface import DeepFace
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
from typing import List, Dict, Optional, Union

class ImageProcessor:
    """Handles all image-related operations"""
    
    @staticmethod
    def load_image(input_path: str) -> np.ndarray:
        """Load image from either URL or local file"""
        if input_path.startswith(('http://', 'https://')):
            # Download from URL
            resp = requests.get(input_path)
            if resp.status_code != 200:
                raise ValueError(f"Failed to download image from URL. Status code: {resp.status_code}")
            image = np.asarray(bytearray(resp.content), dtype="uint8")
            img = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            # Load from local file
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Image file not found: {input_path}")
            img = cv2.imread(input_path)
        
        if img is None:
            raise ValueError("Could not load the image (invalid image file)")
        
        return img

    @staticmethod
    def has_human_face(img_path: str) -> bool:
        """Check if an image contains a human face"""
        try:
            for backend in ['retinaface']: # ["opencv", "ssd", "mtcnn", "retinaface"]:
                try:
                    face_objs = DeepFace.extract_faces(
                        img_path, 
                        detector_backend=backend, 
                        enforce_detection=False
                    )
                    if len(face_objs) > 0 and face_objs[0]['confidence'] > 0.9:
                        return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"Error in face detection: {e}")
            return False

    @staticmethod
    def compare_faces(target_img: np.ndarray, profile_img_url: str) -> float:
        """
        Compare two faces and return similarity score (lower = better match)
        Returns float('inf') if comparison fails
        """
        try:
            # Download profile image
            profile_img = ImageProcessor.load_image(profile_img_url)
            
            # Save temporarily (DeepFace works better with file paths)
            target_path = "temp_target.jpg"
            profile_path = "temp_profile.jpg"
            cv2.imwrite(target_path, target_img)
            cv2.imwrite(profile_path, profile_img)
            
            # Verify both images contain human faces
            if not ImageProcessor.has_human_face(target_path):
                print("Target image doesn't contain a clear human face")
                return float('inf')
                
            if not ImageProcessor.has_human_face(profile_path):
                print("Profile image doesn't contain a clear human face")
                return float('inf')
            
            # Compare using Facenet
            try:
                result = DeepFace.verify(
                    img1_path=target_path, 
                    img2_path=profile_path,
                    model_name="Facenet",
                    distance_metric="cosine",
                    detector_backend="retinaface",
                    enforce_detection=False
                )
                distance = result['distance']
            except Exception as e:
                print(f"Error comparing faces: {e}")
                distance = float('inf')
            
            # Clean up temp files
            if os.path.exists(target_path):
                os.remove(target_path)
            if os.path.exists(profile_path):
                os.remove(profile_path)
                
            return distance
        
        except Exception as e:
            print(f"Error in compare_faces: {e}")
            # Clean up temp files if they exist
            if 'target_path' in locals() and os.path.exists(target_path):
                os.remove(target_path)
            if 'profile_path' in locals() and os.path.exists(profile_path):
                os.remove(profile_path)
            return float('inf')


class FacebookScraper:
    """Handles all Facebook scraping operations"""
    
    def __init__(self, username: str, password: str, driver_path: str = r"C:\Users\nuixalam\Desktop\FacebookScraper\facebook_scraper_app\chromedriver\chromedriver.exe", driver=None):
        self.username = username
        self.password = password
        self.driver_path = driver_path
        self.driver = driver  # Accept an existing driver instance
        self._external_driver = driver is not None
        
    def __enter__(self):
        """Context manager entry - initialize the driver if not provided"""
        if self.driver is None:
            self._initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - do not close driver if it was passed in from outside"""
        if self.driver and not self._external_driver:
            self.driver.quit()
    
    def _initialize_driver(self):
        """Initialize the Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(
            service=Service(self.driver_path), 
            options=chrome_options
        )
    
    def login(self):
        """Log in to Facebook"""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        self.driver.get("https://www.facebook.com")
        time.sleep(3)
        self.driver.refresh()
        time.sleep(3)
        
        try:
            self.driver.find_element(By.ID, "email").send_keys(self.username)
            time.sleep(3)
            self.driver.find_element(By.ID, "pass").send_keys(self.password)
            time.sleep(3)
            self.driver.find_element(By.NAME, "login").click()
            time.sleep(7)
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    @staticmethod
    def clean_facebook_url(url: str) -> str:
        """Clean Facebook URL by removing tracking parameters"""
        if 'profile.php?id=' in url:
            return url.split('&')[0]
        return url.split('?')[0]
    
    def scrape_profiles(self, search_query: str, max_profiles: int = 25) -> List[Dict]:
        """
        Scrape Facebook for profiles matching the search query
        
        Args:
            search_query: Name to search for
            max_profiles: Maximum number of profiles to return
            
        Returns:
            List of profile dictionaries with url, profile_pic, and name
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        profiles_data = []
        
        try:
            # Search for the person
            search_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='search']")
            search_field.clear()
            search_field.send_keys(search_query)
            time.sleep(1)
            search_field.send_keys(Keys.RETURN)
            time.sleep(3)
            
            try:
                # Use the full HTML structure you provided to find the 'See all' button
                see_all_button = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'xdj266r') and contains(@class, 'xat24cr') and contains(@class, 'xexx8yu') and contains(@class, 'xyri2b') and contains(@class, 'x18d9i69') and contains(@class, 'x1c1uobl') and contains(@class, 'x6s0dn4') and contains(@class, 'x78zum5') and contains(@class, 'xl56j7k') and contains(@class, 'x14ayic') and contains(@class, 'xwyz465') and contains(@class, 'x1e0frkt')]//span[contains(text(), 'See all')]"
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", see_all_button)
                time.sleep(1)
                try:
                    see_all_button.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", see_all_button)
                time.sleep(4)
            except Exception as e:
                print(f"No 'See all' button found or could not click it: {e}")

            # Scroll down three times to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for content to load

            # Wait for profile links
            wait = WebDriverWait(self.driver, 10)
            links = wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, 
                'div.x193iq5w.x1xwk8fm span.xjp7ctv > a[href*="facebook.com"]'
            )))

            # Get unique URLs in order of appearance
            unique_urls = []
            for link in links:
                url = link.get_attribute("href")
                clean_url = self.clean_facebook_url(url)
                if clean_url not in unique_urls:
                    unique_urls.append(clean_url)

            # Visit each profile and extract data
            for url in unique_urls[:max_profiles]:
                try:
                    profile_data = {'url': url, 'profile_pic': None, 'name': None}
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # Get profile name
                    try:
                        # Use the full class list for the h1 element as in the provided HTML
                        name_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.x1e56ztr > span > h1.xdj266r.x1lziwak")))
                        profile_data['name'] = name_element.text.split("&nbsp;")[0].strip()
                    except Exception as e:
                        print(f"Could not get name for {url}: {e}")
                    
                    # Get profile picture
                    try:
                        img_element = self.driver.find_element(By.XPATH, 
                            "//img[contains(@class, 'x1ey2m1c') and contains(@class, 'xds687c')]")
                        profile_data['profile_pic'] = img_element.get_attribute('src')
                    except:
                        try:
                            # Alternative method for profile picture
                            parent_container = self.driver.find_element(By.XPATH, 
                                "//div[contains(@class, 'x1jx94hy') and contains(@class, 'x1c9tyrk')]")
                            profile_pic_div = parent_container.find_element(
                                By.XPATH, ".//div[contains(@class, 'x1rg5ohu')]")
                            svg = profile_pic_div.find_element(By.TAG_NAME, "svg")
                            image = svg.find_element(By.TAG_NAME, "image")
                            profile_data['profile_pic'] = image.get_attribute("xlink:href") or image.get_attribute("href")
                        except Exception as e:
                            print(f"Could not extract profile picture for {url}: {e}")
                    
                    if profile_data['profile_pic']:
                        profiles_data.append(profile_data)
                        print(f"Found profile: {profile_data['name'] or 'Unknown name'}")
                        
                except Exception as e:
                    print(f"Error processing profile {url}: {e}")
                    continue 

        except Exception as e:
            print(f"Error during scraping: {e}")
        
        return profiles_data


class NameVariantGenerator:
    """Generates name variants for more comprehensive searching"""
    
    @staticmethod
    def generate_variants(full_name: str) -> List[str]:
        """
        Generate common name variants for searching
        
        Args:
            full_name: The complete name to generate variants from
            
        Returns:
            List of name variants to use in searches
        """
        parts = full_name.split()
        variants = set()

        # Always include the full name
        variants.add(full_name)
        
        # Handle hyphenated last names (like "Sone-Martinez")
        hyphenated = any('-' in part for part in parts)
        
        if hyphenated:
            # For hyphenated names, generate:
            # 1. Full name (Jose Sone-Martinez)
            # 2. First name + first part of hyphenated (Jose Sone)
            # 3. First name + second part of hyphenated (Jose Martinez)
            for part in parts:
                if '-' in part:
                    hyphen_parts = part.split('-')
                    # First name + first part of hyphenated
                    variants.add(f"{parts[0]} {hyphen_parts[0]}")
                    # First name + second part of hyphenated
                    variants.add(f"{parts[0]} {hyphen_parts[1]}")
        else:
            # For non-hyphenated names with exactly 3 parts (Ferlin Adames Banks)
            if len(parts) == 3:
                # First name + middle name (Ferlin Adames)
                variants.add(f"{parts[0]} {parts[1]}")
                # First name + last name (Ferlin Banks)
                variants.add(f"{parts[0]} {parts[2]}")
            # For non-hyphenated names with exactly 2 parts (John Smith)
            elif len(parts) == 2:
                # Just keep the full name (already added)
                pass
        
        return list(variants)


class FaceMatcher:
    """Main class that coordinates the face matching process"""
    
    def __init__(self, facebook_username: str, facebook_password: str, driver=None):
        self.facebook_username = facebook_username
        self.facebook_password = facebook_password
        self.driver = driver  # Accept an existing driver instance
    
    def find_matches(
        self,
        target_image: Union[str, np.ndarray],
        full_name: str,
        top_k: int = 3,
        max_profiles_per_variant: int = 25
    ) -> List[Dict]:
        """
        Find the top matching Facebook profiles for a given face and name
        
        Args:
            target_image: Either a URL, file path, or numpy array of the target image
            full_name: Full name of the person to search for
            top_k: Number of top matches to return
            max_profiles_per_variant: Maximum profiles to fetch per name variant
            
        Returns:
            List of profile dictionaries sorted by match quality (best first)
        """
        # Load target image
        if isinstance(target_image, str):
            target_img = ImageProcessor.load_image(target_image)
        elif isinstance(target_image, np.ndarray):
            target_img = target_image
        else:
            raise ValueError("target_image must be either a string (URL/path) or numpy array")
        
        # Verify target image has a human face
        cv2.imwrite("temp_target_check.jpg", target_img)
        if not ImageProcessor.has_human_face("temp_target_check.jpg"):
            print("Target image doesn't contain a clear human face. Exiting.")
            if os.path.exists("temp_target_check.jpg"):
                os.remove("temp_target_check.jpg")
            return []
        if os.path.exists("temp_target_check.jpg"):
            os.remove("temp_target_check.jpg")
        
        # Generate name variants
        name_variants = NameVariantGenerator.generate_variants(full_name)
        all_profiles_data = []
        
        # Scrape Facebook for each name variant
        with FacebookScraper(self.facebook_username, self.facebook_password, driver=self.driver) as scraper:
            # Only login if we created the driver here
            if self.driver is None:
                if not scraper.login():
                    print("Failed to login to Facebook")
                    return []

            for variant in name_variants:
                print(f"Scraping Facebook profiles for: {variant}")
                profiles_data = scraper.scrape_profiles(variant, max_profiles_per_variant)
                all_profiles_data.extend(profiles_data)
        
        if not all_profiles_data:
            print("No profiles found with pictures.")
            return []
        
        # Remove duplicate profiles based on URL
        unique_profiles = {}
        for profile in all_profiles_data:
            if profile['url'] not in unique_profiles:
                unique_profiles[profile['url']] = profile
        
        unique_profiles_list = list(unique_profiles.values())
        
        print(f"\nFound {len(unique_profiles_list)} unique profiles to compare")
        
        # Compare each profile picture with target
        print("\nComparing faces...")
        for profile in unique_profiles_list:
            try:
                distance = ImageProcessor.compare_faces(target_img, profile['profile_pic'])
                profile['distance'] = distance
                print(f"Compared with {profile['name'] or 'Unknown'}: distance = {distance:.4f}")
            except Exception as e:
                print(f"Error processing {profile['url']}: {e}")
                profile['distance'] = float('inf')
        
        # Filter and sort results
        valid_profiles = [p for p in unique_profiles_list if 'distance' in p and p['distance'] != float('inf')]
        valid_profiles.sort(key=lambda x: x['distance'])
        
        return valid_profiles[:top_k]