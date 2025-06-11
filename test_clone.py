import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from pathlib import Path
import hashlib
import concurrent.futures
from tqdm import tqdm
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

class WebsiteCloner:
    def __init__(self):
        self.web_dir = "web"
        self.pages_dir = os.path.join(self.web_dir, "pages")
        self.assets_dir = os.path.join(self.web_dir, "assets", "images")
        self.image_mapping = {}
        self.session = self._create_session()
        self.setup_logging()
        
        # Load all pages from validation report
        self.page_mapping = self._load_page_mapping()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('clone.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _create_session(self):
        """Create a session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504, 404]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _load_page_mapping(self):
        """Load page mappings from the validation report"""
        try:
            with open('master_validation_report.json', 'r') as f:
                data = json.load(f)
                
            # Get the original base URL
            base_url = data['site_info']['original_base']
            
            # Extract all unique pages from navigation links and banner usage
            pages = set()
            
            # Add pages from navigation links
            nav_links = data['test_results']['functional']['navigation_test']['navigation_links']
            for page_links in nav_links.values():
                pages.update(page_links)
            
            # Add pages from banner usage
            banner_usage = data['test_results']['functional']['banner_consistency_test']['banner_usage']
            for page_list in banner_usage.values():
                pages.update(page_list)
            
            # Create mapping of page names to full URLs (keep .html extension)
            page_mapping = {}
            for page in pages:
                page_mapping[page] = urljoin(base_url, page)
            
            self.logger.info(f"Loaded {len(page_mapping)} pages from validation report")
            return page_mapping
        except Exception as e:
            self.logger.error(f"Error loading page mapping: {e}")
            return {}

    def setup_directories(self):
        """Create the necessary directory structure"""
        for directory in [self.pages_dir, self.assets_dir]:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")

    def download_file(self, url, save_path):
        """Download a file and save it to the specified path"""
        try:
            self.logger.debug(f"Downloading: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return False

    def process_image(self, img_url, page_url):
        """Process an image URL and return the new local path"""
        if img_url in self.image_mapping:
            return self.image_mapping[img_url]

        # Generate a unique filename for the image
        parsed_url = urlparse(img_url)
        original_filename = os.path.basename(parsed_url.path)
        filename, ext = os.path.splitext(original_filename)
        
        # Create a hash of the URL to handle duplicates
        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
        new_filename = f"{filename}_{url_hash}{ext}"
        
        # Download the image
        local_path = os.path.join(self.assets_dir, new_filename)
        full_url = urljoin(page_url, img_url)
        
        if self.download_file(full_url, local_path):
            # Store the mapping
            self.image_mapping[img_url] = new_filename
            return new_filename
        return None

    def process_page(self, page_name):
        """Process a single page and its resources"""
        if page_name not in self.page_mapping:
            self.logger.warning(f"No URL mapping found for {page_name}")
            return False

        page_url = self.page_mapping[page_name]
        local_path = os.path.join(self.pages_dir, page_name)
        
        self.logger.info(f"Processing page: {page_url} -> {local_path}")
        
        # Download the page
        if not self.download_file(page_url, local_path):
            return False

        # Parse the page
        with open(local_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Process images
        for img in soup.find_all('img'):
            if img.get('src'):
                new_img_path = self.process_image(img['src'], page_url)
                if new_img_path:
                    img['src'] = f"../assets/images/{new_img_path}"

        # Process image maps
        for map_tag in soup.find_all('map'):
            for area in map_tag.find_all('area'):
                if area.get('href'):
                    # Convert absolute URLs to relative
                    if area['href'].startswith('https://0002n8y.wcomhost.com/website/'):
                        area['href'] = area['href'].replace('https://0002n8y.wcomhost.com/website/', '')

        # Save the modified page
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        return True

    def process_page_with_progress(self, page):
        """Wrapper for process_page to work with progress bar"""
        return self.process_page(page)

    def run_full_clone(self):
        """Run the full site clone with progress bars"""
        self.logger.info("Starting full site clone")
        self.setup_directories()
        
        all_pages = list(self.page_mapping.keys())
        self.logger.info(f"Found {len(all_pages)} pages to process")
        
        # Process pages with progress bar
        with tqdm(total=len(all_pages), desc="Processing pages") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all tasks
                future_to_page = {
                    executor.submit(self.process_page_with_progress, page): page 
                    for page in all_pages
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        success = future.result()
                        if not success:
                            self.logger.warning(f"Failed to process {page}")
                    except Exception as e:
                        self.logger.error(f"Error processing {page}: {e}")
                    pbar.update(1)

        # Save the image mapping for reference
        with open(os.path.join(self.web_dir, 'image_mapping.json'), 'w') as f:
            json.dump(self.image_mapping, f, indent=2)
        
        self.logger.info("Site clone completed")
        self.logger.info(f"Downloaded {len(self.image_mapping)} images")

if __name__ == "__main__":
    cloner = WebsiteCloner()
    cloner.run_full_clone() 