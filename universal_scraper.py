"""
Universal Web Scraper - Extract company names from any website
Intelligent scraper that detects pagination and company names automatically
"""

import re
import time
import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalScraper:
    """Universal scraper for extracting company names from any website"""

    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.companies = []
        self.visited_urls = set()

        # Common company name patterns
        self.company_indicators = [
            'company', 'entreprise', 'exhibitor', 'exposant', 'vendor',
            'supplier', 'fournisseur', 'partner', 'partenaire', 'member',
            'société', 'business', 'firm', 'organization'
        ]

        # Pagination indicators
        self.pagination_indicators = [
            'next', 'suivant', 'page', '>>', '›', 'more', 'plus',
            'pagination', 'nav'
        ]

    def setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)

    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

    def extract_company_names(self, html):
        """
        Intelligently extract company names from HTML
        STRICT MODE: Only real company names, no navigation/menu items
        """
        soup = BeautifulSoup(html, 'lxml')
        found_companies = []

        # Strategy 1: Links that look like company profiles (MOST RELIABLE)
        # Pattern: /fabricant/nom, /company/nom, /entreprise/nom, -s1234.html
        profile_patterns = [
            r'/fabricant/[^/]+',
            r'/company/[^/]+',
            r'/entreprise/[^/]+',
            r'/exposant/[^/]+',
            r'/member/[^/]+',
            r'-s\d+\.html',
            r'/fournisseur/[^/]+',
            r'/supplier/[^/]+'
        ]

        for pattern in profile_patterns:
            links = soup.find_all('a', href=re.compile(pattern, re.I))
            for link in links:
                # Get text from link or title attribute
                text = link.get_text(strip=True) or link.get('title', '').strip()
                if text and 3 <= len(text) <= 150:
                    found_companies.append(text)

        # Strategy 2: Links with title attributes (ONLY if href looks like company profile)
        titled_links = soup.find_all('a', title=True, href=True)
        for link in titled_links:
            href = link.get('href', '')

            # Skip navigation links
            if any(nav in href.lower() for nav in ['/news', '/blog', '/contact', '/about',
                                                     '/articles', '/actualites', '/search',
                                                     '/login', '/mon-compte', '/profile']):
                continue

            # Only keep if href looks like a company profile
            if any(pattern in href.lower() for pattern in ['/fabricant/', '/company/',
                                                             '/entreprise/', '/exposant/',
                                                             '/member/', '/fournisseur/',
                                                             '/supplier/']):
                title = link.get('title', '').strip()
                text = link.get_text(strip=True)

                # Prefer title if it looks like a company name
                if title and 3 <= len(title) <= 150:
                    found_companies.append(title)
                elif text and 3 <= len(text) <= 150:
                    found_companies.append(text)

        # Strategy 3: Lists with many items (ONLY if items have company profile links)
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            if len(items) > 10:  # Higher threshold - must be a real directory
                for item in items:
                    # MUST have a link
                    link = item.find('a', href=True)
                    if not link:
                        continue

                    href = link.get('href', '')

                    # Skip navigation
                    if any(nav in href.lower() for nav in ['/news', '/blog', '/actualites',
                                                             '/articles', '/contact']):
                        continue

                    # Get text
                    text = link.get_text(strip=True) or link.get('title', '').strip()

                    if text and 3 <= len(text) <= 150:
                        found_companies.append(text)

        # Strategy 4: Structured containers with company indicators (STRICT)
        for indicator in self.company_indicators:
            containers = soup.find_all(class_=re.compile(indicator, re.I))

            for container in containers:
                # ONLY get links from these containers
                links = container.find_all('a', href=True)
                for link in links[:5]:  # Max 5 links per container
                    href = link.get('href', '')

                    # MUST look like a company profile link
                    if not any(pattern in href.lower() for pattern in ['/fabricant/', '/company/',
                                                                         '/entreprise/', '/exposant/',
                                                                         '/member/', '/fournisseur/',
                                                                         '/supplier/', '-s']):
                        continue

                    text = link.get_text(strip=True)
                    if text and 3 <= len(text) <= 150:
                        found_companies.append(text)

        # Strategy 5: Table rows (ONLY with company profile links)
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 10:  # Higher threshold
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        first_cell = cells[0]
                        link = first_cell.find('a', href=True)
                        if link:
                            href = link.get('href', '')
                            # Must be a company profile
                            if any(p in href.lower() for p in ['/fabricant/', '/company/', '/exposant/']):
                                text = link.get_text(strip=True) or link.get('title', '').strip()
                                if text and 3 <= len(text) <= 150:
                                    found_companies.append(text)

        # Strategy 6: Cards (modern layouts) - STRICT
        cards = soup.find_all(['article', 'div'], class_=re.compile('card|item|box|result|listing|exhibitor', re.I))
        for card in cards:
            # MUST have a link that looks like a company profile
            link = card.find('a', href=True)
            if not link:
                continue

            href = link.get('href', '')
            if not any(p in href.lower() for p in ['/fabricant/', '/company/', '/exposant/', '/entreprise/', '-s']):
                continue

            # Get text from heading or link
            title = card.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if title:
                text = title.get_text(strip=True)
            else:
                text = link.get_text(strip=True) or link.get('title', '').strip()

            if text and 3 <= len(text) <= 150:
                found_companies.append(text)

        # Clean and deduplicate with advanced filtering
        cleaned = []
        seen = set()

        # STRICT BLACKLIST - Everything that is NOT a company name
        blacklist = {
            # Navigation
            'home', 'contact', 'about', 'menu', 'search', 'login', 'accueil',
            'connexion', 'recherche', 'à propos', 'mentions légales', 'cookies',
            'politique', 'confidentialité', 'conditions', 'cgv', 'cgu',
            'afficher', 'show', 'hide', 'masquer', 'tout', 'all',

            # Actions
            'voir', 'plus', 'more', 'details', 'détails', 'lire la suite', 'read more',
            'en savoir plus', 'découvrir', 'discover', 'voir tout', 'see all',

            # Pagination
            'page', 'suivant', 'précédent', 'next', 'previous', 'retour', 'back',
            'first', 'last', 'premier', 'dernier',

            # Navigation française (batiweb style)
            'toutes les actualités', 'communiqués', 'dossiers spéciaux',
            'vie des sociétés', 'immobilier', 'architecture', 'patrimoine',
            'urbanisme', 'construction', 'énergie', 'conjoncture',
            'développement durable', 'marchés publics', 'événements et salons',
            'mon profil', 'déconnexion', 'mon compte', 'mes newsletters',
            'mes indices-index', 'mes articles', 'mes produits', 'mes communiqués',
            'mes vidéos', 'budget', 'maprimerenov', 'rénovation énergétique',
            'fraudes', 'zan',

            # Sections génériques
            'actualités', 'news', 'articles', 'produits', 'products',
            'services', 'solutions', 'about us', 'qui sommes-nous',
            'notre histoire', 'nos valeurs', 'équipe', 'team',
            'carrières', 'careers', 'emploi', 'jobs',
            'presse', 'press', 'médias', 'media',
            'blog', 'newsletter', 'inscription', 'subscribe',
            'télécharger', 'download', 'documentation', 'ressources',
            'faq', 'aide', 'help', 'support', 'tutoriels',
            'légal', 'legal', 'privacy', 'terms',

            # Actions génériques
            'cliquez ici', 'click here', 'en savoir plus', 'learn more',
            'contactez-nous', 'contact us', 'demander un devis', 'get a quote',
            'inscription gratuite', 'free trial', 'essai gratuit',

            # Catégories
            'catégories', 'categories', 'rubriques', 'sections',
            'tous les fabricants', 'all manufacturers', 'annuaire',
            'directory', 'liste', 'list',

            # Mots isolés trop génériques
            'nouveau', 'new', 'hot', 'top', 'best', 'meilleur',
            'gratuit', 'free', 'offre', 'offer', 'promo', 'promotion'
        }

        # Prefixes to remove
        prefixes_to_remove = ['détails :', 'details:', 'voir:', 'see:']

        for company in found_companies:
            # Clean the text
            company = re.sub(r'\s+', ' ', company).strip()

            # Remove common prefixes
            for prefix in prefixes_to_remove:
                if company.lower().startswith(prefix):
                    company = company[len(prefix):].strip()

            # Remove leading/trailing punctuation
            company = company.strip('.-,;:|[](){}')

            # Skip if empty after cleaning
            if not company:
                continue

            # Skip if too short or too long
            if len(company) < 3 or len(company) > 150:
                continue

            # Skip blacklisted terms
            if company.lower() in blacklist:
                continue

            # Skip if it's a number
            if company.isdigit():
                continue

            # Skip if it's mostly numbers (like "Page 2")
            if sum(c.isdigit() for c in company) / len(company) > 0.5:
                continue

            # Skip URLs
            if 'http' in company.lower() or 'www.' in company.lower():
                continue

            # Deduplicate (case insensitive)
            company_lower = company.lower()
            if company_lower not in seen:
                cleaned.append(company)
                seen.add(company_lower)

        return cleaned

    def find_pagination_links(self, current_url):
        """
        Find pagination links with intelligent pattern detection
        Supports multiple pagination styles
        """
        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            pagination_links = []
            parsed_url = urlparse(current_url)

            # Strategy 1: Pattern-based URL pagination (e.g., -p1.html, -p2.html)
            # Extract current page number from URL
            url_patterns = [
                (r'-p(\d+)\.html', '-p{}.html'),  # batiment.eu style
                (r'/page/(\d+)', '/page/{}'),
                (r'[?&]page=(\d+)', '?page={}'),
                (r'/p(\d+)/', '/p{}/'),
            ]

            current_page = 1
            pattern_match = None

            for pattern, template in url_patterns:
                match = re.search(pattern, current_url)
                if match:
                    current_page = int(match.group(1))
                    pattern_match = (pattern, template)
                    break

            # Generate next pages using detected pattern
            if pattern_match:
                pattern, template = pattern_match
                for next_page in range(current_page + 1, current_page + 6):  # Next 5 pages
                    # Replace page number in URL
                    next_url = re.sub(pattern, template.format(next_page), current_url)
                    if next_url != current_url and next_url not in self.visited_urls:
                        pagination_links.append(next_url)

            # Strategy 2: Standard pagination links (Next, numbers, etc.)
            # Look for "next" links
            next_selectors = [
                'a[rel="next"]',
                'a.next',
                'a.pagination-next',
                'li.next a',
                'a[aria-label*="next" i]',
                'a[title*="next" i]',
                'a[title*="suivant" i]'
            ]

            for selector in next_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and href != '#':
                        absolute_url = urljoin(current_url, href)
                        if absolute_url not in self.visited_urls and absolute_url not in pagination_links:
                            pagination_links.append(absolute_url)

            # Strategy 3: Numbered pagination links
            # Find links that are just numbers
            number_links = soup.find_all('a', string=re.compile(r'^\s*\d+\s*$'))
            for link in number_links:
                href = link.get('href')
                if href and href != '#':
                    # Only add if number is greater than current page
                    try:
                        page_num = int(link.get_text(strip=True))
                        if page_num > current_page:
                            absolute_url = urljoin(current_url, href)
                            if absolute_url not in self.visited_urls and absolute_url not in pagination_links:
                                pagination_links.append(absolute_url)
                    except:
                        pass

            # Strategy 4: Generic "Next" text links
            for indicator in ['next', 'suivant', 'page suivante', 'next page', '›', '»', '>']:
                links = soup.find_all('a', string=re.compile(re.escape(indicator), re.I))
                for link in links:
                    href = link.get('href')
                    if href and href != '#':
                        absolute_url = urljoin(current_url, href)
                        if absolute_url not in self.visited_urls and absolute_url not in pagination_links:
                            pagination_links.append(absolute_url)

            # Strategy 5: Selenium-based "Next" button click detection
            try:
                next_button_xpaths = [
                    "//a[contains(@class, 'next')]",
                    "//a[contains(text(), 'Suivant')]",
                    "//a[contains(text(), 'Next')]",
                    "//button[contains(@class, 'next')]",
                    "//a[@rel='next']"
                ]

                for xpath in next_button_xpaths:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, xpath)
                        for btn in buttons[:2]:  # Max 2 buttons
                            href = btn.get_attribute('href')
                            if href and href not in self.visited_urls and href not in pagination_links:
                                pagination_links.append(href)
                    except:
                        continue
            except:
                pass

            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in pagination_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)

            # Limit to reasonable number of pages
            return unique_links[:10]

        except Exception as e:
            logger.debug(f"Error finding pagination: {e}")
            return []

    def scrape_url(self, url, max_pages=10, progress_callback=None):
        """
        Scrape a URL and automatically handle pagination

        Args:
            url: Starting URL
            max_pages: Maximum number of pages to scrape
            progress_callback: Function to call with progress updates

        Returns:
            List of company names
        """
        logger.info(f"Starting scrape of: {url}")

        if not self.driver:
            self.setup_driver()

        self.companies = []
        self.visited_urls = set()
        pages_to_visit = [url]
        pages_scraped = 0

        while pages_to_visit and pages_scraped < max_pages:
            current_url = pages_to_visit.pop(0)

            if current_url in self.visited_urls:
                continue

            try:
                logger.info(f"Scraping page {pages_scraped + 1}: {current_url}")

                if progress_callback:
                    progress_callback(pages_scraped + 1, max_pages, f"Scraping: {current_url[:50]}...")

                # Load the page
                self.driver.get(current_url)
                time.sleep(2)  # Wait for JavaScript

                # Accept cookies if present
                self.accept_cookies()

                # Scroll to load lazy content
                self.scroll_page()

                # Extract company names
                html = self.driver.page_source
                companies = self.extract_company_names(html)

                logger.info(f"Found {len(companies)} potential companies on this page")
                self.companies.extend(companies)

                # Mark as visited
                self.visited_urls.add(current_url)
                pages_scraped += 1

                # Find pagination links for next pages
                if pages_scraped < max_pages:
                    next_links = self.find_pagination_links(current_url)
                    pages_to_visit.extend(next_links)

                time.sleep(1)  # Be respectful

            except Exception as e:
                logger.error(f"Error scraping {current_url}: {e}")
                continue

        # Deduplicate final results
        unique_companies = list(dict.fromkeys(self.companies))

        logger.info(f"Total unique companies found: {len(unique_companies)}")
        return unique_companies

    def accept_cookies(self):
        """Try to accept cookie consent"""
        try:
            cookie_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Accepter')]",
                "//button[contains(text(), 'OK')]",
                "//a[contains(text(), 'Accept')]",
                "//button[contains(@class, 'accept')]",
                "//button[contains(@id, 'accept')]"
            ]

            for selector in cookie_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(0.5)
                    return
                except:
                    continue
        except:
            pass

    def scroll_page(self):
        """Scroll page to trigger lazy loading"""
        try:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
        except:
            pass


def scrape_companies_from_url(url, max_pages=10, progress_callback=None):
    """
    Convenience function to scrape companies from a URL

    Args:
        url: Starting URL
        max_pages: Maximum pages to scrape
        progress_callback: Optional callback for progress updates

    Returns:
        List of company dictionaries with 'name' key
    """
    scraper = UniversalScraper(headless=True)

    try:
        company_names = scraper.scrape_url(url, max_pages, progress_callback)

        # Convert to standard format
        companies = [{'name': name} for name in company_names]

        return companies

    finally:
        scraper.close()


if __name__ == '__main__':
    # Test the universal scraper
    test_url = input("Enter URL to scrape: ")
    max_pages = int(input("Max pages (1-20): ") or "3")

    companies = scrape_companies_from_url(test_url, max_pages)

    print(f"\n✅ Found {len(companies)} companies:")
    for i, company in enumerate(companies[:20], 1):
        print(f"{i}. {company['name']}")

    if len(companies) > 20:
        print(f"... and {len(companies) - 20} more")
