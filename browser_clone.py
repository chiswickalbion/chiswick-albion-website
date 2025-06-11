import json
import os
import time
import logging
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clone.log'),
        logging.StreamHandler()
    ]
)

class BrowserSiteCloner:
    def __init__(self, validation_report_path):
        self.validation_report_path = validation_report_path
        self.page_mapping = {}
        self.image_mapping = {}
        self.web_dir = Path('web')
        self.pages_dir = self.web_dir / 'pages'
        self.images_dir = self.web_dir / 'assets' / 'images'
        
    def _load_page_mapping(self):
        """Load page mapping from validation report."""
        try:
            with open(self.validation_report_path, 'r') as f:
                report = json.load(f)
            
            # Get the base URL from the report
            base_url = report['site_info']['original_base']
            
            # Collect all unique pages from navigation links and banner usage
            pages = set()
            
            # Add pages from navigation links
            nav_links = report['test_results']['functional']['navigation_test']['navigation_links']
            for page_links in nav_links.values():
                pages.update(page_links)
            
            # Add pages from banner usage
            banner_usage = report['test_results']['functional']['banner_consistency_test']['banner_usage']
            for page_list in banner_usage.values():
                pages.update(page_list)
            
            # Create mapping of page names to full URLs
            self.page_mapping = {
                page: urljoin(base_url, page)
                for page in pages
            }
            
            logging.info(f"Loaded {len(self.page_mapping)} pages from validation report")
            
        except Exception as e:
            logging.error(f"Error loading validation report: {e}")
            raise

    def _create_directories(self):
        """Create necessary directories for the cloned site."""
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {self.pages_dir}")
        logging.info(f"Created directory: {self.images_dir}")

    async def _download_page(self, page_name, url):
        """Download a single page and its resources using Playwright."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate to the page
                response = await page.goto(url)
                if not response:
                    logging.error(f"Failed to load {url}")
                    return
                
                if response.status != 200:
                    logging.error(f"Failed to load {url}: HTTP {response.status}")
                    return
                
                # Get the page content
                content = await page.content()
                
                # Save the HTML
                output_path = self.pages_dir / page_name
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Download images
                images = await page.query_selector_all('img')
                for img in images:
                    src = await img.get_attribute('src')
                    if not src:
                        continue
                    
                    # Convert relative URLs to absolute
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(url, src)
                    
                    # Generate a unique filename for the image
                    image_name = f"img{len(self.image_mapping)}.gif"
                    self.image_mapping[src] = image_name
                    
                    # Download the image
                    try:
                        img_response = await page.goto(src)
                        if img_response and img_response.status == 200:
                            img_data = await img_response.body()
                            with open(self.images_dir / image_name, 'wb') as f:
                                f.write(img_data)
                    except Exception as e:
                        logging.error(f"Error downloading image {src}: {e}")
                
                await browser.close()
                
        except Exception as e:
            logging.error(f"Error processing {url}: {e}")

    async def run_full_clone(self):
        """Run the full site cloning process."""
        self._load_page_mapping()
        self._create_directories()
        
        logging.info("Starting full site clone")
        logging.info(f"Found {len(self.page_mapping)} pages to process")
        
        # Process pages concurrently
        tasks = []
        for page_name, url in self.page_mapping.items():
            tasks.append(self._download_page(page_name, url))
        
        await asyncio.gather(*tasks)
        
        # Save image mapping
        with open(self.web_dir / 'image_mapping.json', 'w') as f:
            json.dump(self.image_mapping, f, indent=2)
        
        logging.info("Site clone completed")
        logging.info(f"Downloaded {len(self.image_mapping)} images")

if __name__ == "__main__":
    cloner = BrowserSiteCloner('master_validation_report.json')
    asyncio.run(cloner.run_full_clone()) 