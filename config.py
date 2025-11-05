"""
Configuration file for the web scraper
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Selenium settings
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))

# Scraping settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2.0'))

# Proxy settings (optional)
USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'
PROXY_HOST = os.getenv('PROXY_HOST', '')
PROXY_PORT = os.getenv('PROXY_PORT', '')

# Export settings
EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'json')  # json, csv, excel, all
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')

# User agent rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]
