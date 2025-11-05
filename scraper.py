"""
Advanced Web Scraper for JavaScript-rendered websites
"""
import json
import csv
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from colorama import Fore, Style, init
from tqdm import tqdm
import config

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebScraper:
    """Advanced web scraper with Selenium support"""

    def __init__(self, headless: bool = None):
        """
        Initialize the web scraper

        Args:
            headless: Run browser in headless mode (default: from config)
        """
        self.headless = headless if headless is not None else config.HEADLESS_MODE
        self.driver = None
        self.data = []

        # Create output directory
        Path(config.OUTPUT_DIR).mkdir(exist_ok=True)

    def setup_driver(self):
        """Setup Selenium WebDriver with Chrome"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless=new')

            # Basic options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')

            # Random user agent
            user_agent = random.choice(config.USER_AGENTS)
            chrome_options.add_argument(f'user-agent={user_agent}')

            # Proxy support
            if config.USE_PROXY and config.PROXY_HOST:
                proxy = f"{config.PROXY_HOST}:{config.PROXY_PORT}"
                chrome_options.add_argument(f'--proxy-server={proxy}')
                logger.info(f"Using proxy: {proxy}")

            # Exclude automation flags
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Set timeouts
            self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(config.IMPLICIT_WAIT)

            # Execute stealth JavaScript
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info(f"{Fore.GREEN}WebDriver initialized successfully")

        except Exception as e:
            logger.error(f"{Fore.RED}Failed to initialize WebDriver: {e}")
            raise

    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for an element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {value}")
            return None

    def wait_for_elements(self, by: By, value: str, timeout: int = 10):
        """Wait for multiple elements to be present"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            logger.warning(f"Timeout waiting for elements: {value}")
            return []

    def scroll_to_bottom(self, pause_time: float = 2.0):
        """Scroll to bottom of page to load dynamic content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)

            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

    def handle_iframes(self):
        """Switch to iframes if present"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            if iframes:
                logger.info(f"Found {len(iframes)} iframe(s)")
                for idx, iframe in enumerate(iframes):
                    try:
                        self.driver.switch_to.frame(iframe)
                        logger.info(f"{Fore.CYAN}Switched to iframe {idx}")
                        return True
                    except Exception as e:
                        logger.warning(f"Could not switch to iframe {idx}: {e}")
                        continue
            return False
        except Exception as e:
            logger.error(f"Error handling iframes: {e}")
            return False

    def extract_page_data(self, selectors: Dict[str, str]) -> List[Dict]:
        """
        Extract data from the current page using CSS selectors

        Args:
            selectors: Dictionary mapping field names to CSS selectors

        Returns:
            List of dictionaries containing extracted data
        """
        page_data = []

        try:
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Find container elements (customize based on site structure)
            containers = soup.select(selectors.get('container', 'div.item'))

            logger.info(f"Found {len(containers)} items on page")

            for container in containers:
                item = {}

                for field, selector in selectors.items():
                    if field == 'container':
                        continue

                    try:
                        element = container.select_one(selector)
                        if element:
                            # Try to get text or specific attribute
                            if element.get('href'):
                                item[field] = element.get('href')
                            elif element.get('src'):
                                item[field] = element.get('src')
                            else:
                                item[field] = element.get_text(strip=True)
                        else:
                            item[field] = None
                    except Exception as e:
                        logger.debug(f"Error extracting {field}: {e}")
                        item[field] = None

                if item:
                    page_data.append(item)

        except Exception as e:
            logger.error(f"Error extracting page data: {e}")

        return page_data

    def scrape_url(self, url: str, selectors: Dict[str, str], max_pages: Optional[int] = None) -> List[Dict]:
        """
        Scrape a URL with pagination support

        Args:
            url: Target URL
            selectors: CSS selectors for data extraction
            max_pages: Maximum number of pages to scrape (None = all)

        Returns:
            List of extracted data
        """
        all_data = []
        page_count = 0

        try:
            if not self.driver:
                self.setup_driver()

            logger.info(f"{Fore.CYAN}Starting to scrape: {url}")

            # Load initial page
            self.driver.get(url)
            time.sleep(config.REQUEST_DELAY)

            # Handle iframes if present
            iframe_switched = self.handle_iframes()

            while True:
                page_count += 1
                logger.info(f"{Fore.YELLOW}Scraping page {page_count}...")

                # Wait for content to load
                time.sleep(config.REQUEST_DELAY)

                # Scroll to load dynamic content
                self.scroll_to_bottom(pause_time=1.5)

                # Extract data from current page
                page_data = self.extract_page_data(selectors)
                all_data.extend(page_data)

                logger.info(f"{Fore.GREEN}Extracted {len(page_data)} items from page {page_count}")

                # Check if we've reached max pages
                if max_pages and page_count >= max_pages:
                    logger.info(f"Reached maximum page limit: {max_pages}")
                    break

                # Try to find and click next page button
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selectors.get('next_button', '.next, .pagination-next, [aria-label="Next"]'))

                    if next_button.is_enabled() and next_button.is_displayed():
                        next_button.click()
                        time.sleep(config.REQUEST_DELAY)
                    else:
                        logger.info("Next button not available, pagination complete")
                        break

                except NoSuchElementException:
                    logger.info("No more pages to scrape")
                    break

            logger.info(f"{Fore.GREEN}Scraping complete! Total items: {len(all_data)}")
            self.data = all_data

        except Exception as e:
            logger.error(f"{Fore.RED}Error during scraping: {e}")

        return all_data

    def export_data(self, format: str = None, filename: str = None):
        """
        Export scraped data to file

        Args:
            format: Export format (json, csv, excel, all)
            filename: Base filename (without extension)
        """
        if not self.data:
            logger.warning("No data to export")
            return

        export_format = format or config.EXPORT_FORMAT
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = filename or f'scraped_data_{timestamp}'

        try:
            if export_format in ['json', 'all']:
                json_path = Path(config.OUTPUT_DIR) / f'{base_filename}.json'
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                logger.info(f"{Fore.GREEN}Data exported to {json_path}")

            if export_format in ['csv', 'all']:
                csv_path = Path(config.OUTPUT_DIR) / f'{base_filename}.csv'
                df = pd.DataFrame(self.data)
                df.to_csv(csv_path, index=False, encoding='utf-8')
                logger.info(f"{Fore.GREEN}Data exported to {csv_path}")

            if export_format in ['excel', 'all']:
                excel_path = Path(config.OUTPUT_DIR) / f'{base_filename}.xlsx'
                df = pd.DataFrame(self.data)
                df.to_excel(excel_path, index=False, engine='openpyxl')
                logger.info(f"{Fore.GREEN}Data exported to {excel_path}")

        except Exception as e:
            logger.error(f"{Fore.RED}Error exporting data: {e}")

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


def main():
    """Example usage"""

    # Example selectors for Equipauto exhibitors (you'll need to adjust these)
    selectors = {
        'container': '.exhibitor-item, .exposant-item, .list-item',  # Container selector
        'name': '.name, .company-name, h3, .title',
        'stand': '.stand, .booth, .location',
        'category': '.category, .sector',
        'description': '.description, .about',
        'website': 'a[href*="http"]',
        'email': 'a[href^="mailto:"]',
        'next_button': '.next, .pagination-next, button[aria-label="Next"]'
    }

    # Initialize scraper
    scraper = WebScraper()

    try:
        # Scrape the website
        url = 'https://paris.equipauto.com/liste-des-exposants/'
        data = scraper.scrape_url(url, selectors, max_pages=None)

        # Export data
        scraper.export_data(format='all', filename='equipauto_exhibitors')

    except Exception as e:
        logger.error(f"Scraping failed: {e}")

    finally:
        scraper.close()


if __name__ == '__main__':
    main()
