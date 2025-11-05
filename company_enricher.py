"""
Company Data Enricher - Free & Professional
Extract company and executive contact information from domains

Data Sources (Priority Order):
1. Website Scraping (Free, unlimited)
2. Pappers.fr API (Free: 10,000/month) - French companies
3. Hunter.io API (Free: 50/month) - Email finding

Usage:
    python3 company_enricher.py
"""

import json
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from colorama import Fore, init
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
import os
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompanyEnricher:
    """Enrich company data from domains"""

    def __init__(self, pappers_api_key=None, hunter_api_key=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        # API Keys (optional)
        self.pappers_api_key = pappers_api_key or os.getenv('PAPPERS_API_KEY')
        self.hunter_api_key = hunter_api_key or os.getenv('HUNTER_API_KEY')

        # Stats
        self.stats = {
            'website_scraped': 0,
            'pappers_used': 0,
            'hunter_used': 0,
            'emails_found': 0,
            'phones_found': 0,
            'linkedin_found': 0
        }

        # Regex patterns
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'(?:\+33|0033|0)[1-9](?:[\s.-]?\d{2}){4}'
        )
        self.linkedin_company_pattern = re.compile(
            r'linkedin\.com/company/([^/\s?]+)'
        )
        self.linkedin_profile_pattern = re.compile(
            r'linkedin\.com/in/([^/\s?]+)'
        )

        # Common contact page paths
        self.contact_paths = [
            '/contact', '/contact-us', '/contactez-nous', '/nous-contacter',
            '/about', '/about-us', '/a-propos', '/qui-sommes-nous',
            '/mentions-legales', '/legal', '/impressum', '/imprint'
        ]

    def extract_emails_from_text(self, text):
        """Extract emails from text"""
        emails = self.email_pattern.findall(text.lower())

        # Filter out common noise
        filtered = []
        noise = ['example.com', 'domain.com', 'email.com', 'test.com',
                'yoursite.com', 'yourdomain.com', 'wix.com', 'wordpress.com']

        for email in emails:
            if not any(n in email for n in noise):
                # Prioritize contact/info emails
                if any(word in email for word in ['contact', 'info', 'hello', 'bonjour']):
                    filtered.insert(0, email)
                else:
                    filtered.append(email)

        return list(dict.fromkeys(filtered))  # Remove duplicates, keep order

    def extract_phones_from_text(self, text):
        """Extract French phone numbers from text"""
        phones = self.phone_pattern.findall(text)

        # Normalize format
        normalized = []
        for phone in phones:
            # Remove spaces, dots, dashes
            clean = re.sub(r'[\s.-]', '', phone)
            # Convert to +33 format
            if clean.startswith('0033'):
                clean = '+33' + clean[4:]
            elif clean.startswith('0'):
                clean = '+33' + clean[1:]
            elif not clean.startswith('+'):
                clean = '+33' + clean

            if clean not in normalized:
                normalized.append(clean)

        return normalized

    def extract_linkedin_urls(self, html, base_url):
        """Extract LinkedIn company and profile URLs"""
        soup = BeautifulSoup(html, 'lxml')

        company_linkedin = None
        profile_urls = []

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Company LinkedIn
            match = self.linkedin_company_pattern.search(href)
            if match and not company_linkedin:
                company_linkedin = f"https://linkedin.com/company/{match.group(1)}"

            # Profile LinkedIn
            match = self.linkedin_profile_pattern.search(href)
            if match:
                profile_url = f"https://linkedin.com/in/{match.group(1)}"
                if profile_url not in profile_urls:
                    profile_urls.append(profile_url)

        return company_linkedin, profile_urls

    def scrape_contact_page(self, domain):
        """Scrape website for contact information"""
        result = {
            'emails': [],
            'phones': [],
            'linkedin_company': None,
            'linkedin_profiles': [],
            'method': 'website_scraping'
        }

        try:
            base_url = f"https://{domain}"

            # Try homepage first
            urls_to_try = [base_url]

            # Add contact pages
            for path in self.contact_paths:
                urls_to_try.append(urljoin(base_url, path))

            all_text = ""
            all_html = ""

            for url in urls_to_try[:5]:  # Try first 5 pages
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        all_html += response.text
                        soup = BeautifulSoup(response.text, 'lxml')
                        all_text += soup.get_text() + "\n"
                        time.sleep(0.5)
                except:
                    continue

            if all_text:
                # Extract data
                result['emails'] = self.extract_emails_from_text(all_text)[:3]  # Top 3
                result['phones'] = self.extract_phones_from_text(all_text)[:2]  # Top 2
                result['linkedin_company'], result['linkedin_profiles'] = \
                    self.extract_linkedin_urls(all_html, base_url)

                self.stats['website_scraped'] += 1
                if result['emails']:
                    self.stats['emails_found'] += len(result['emails'])
                if result['phones']:
                    self.stats['phones_found'] += len(result['phones'])
                if result['linkedin_company'] or result['linkedin_profiles']:
                    self.stats['linkedin_found'] += 1

        except Exception as e:
            logger.debug(f"Scraping error for {domain}: {e}")

        return result

    def get_pappers_data(self, company_name, domain):
        """Get company data from Pappers.fr API"""
        if not self.pappers_api_key:
            return None

        try:
            # Search by company name
            url = "https://api.pappers.fr/v2/recherche"
            params = {
                'api_token': self.pappers_api_key,
                'q': company_name,
                'precision': 'standard'
            }

            response = self.session.get(url, params=params, timeout=15)

            # Check for quota exceeded
            if response.status_code == 429:
                logger.warning(f"{Fore.YELLOW}⚠️  Pappers API quota exceeded, continuing without API")
                self.pappers_api_key = None  # Disable for future calls
                return None

            if response.status_code == 200:
                data = response.json()

                if data.get('resultats'):
                    # Get first result
                    company = data['resultats'][0]

                    result = {
                        'siren': company.get('siren'),
                        'siret': company.get('siege', {}).get('siret'),
                        'legal_name': company.get('nom_entreprise'),
                        'address': company.get('siege', {}).get('adresse_ligne_1'),
                        'city': company.get('siege', {}).get('ville'),
                        'postal_code': company.get('siege', {}).get('code_postal'),
                        'executives': [],
                        'method': 'pappers_api'
                    }

                    # Extract executives
                    representants = company.get('representants', [])
                    for rep in representants[:3]:  # Top 3 executives
                        exec_data = {
                            'first_name': rep.get('prenoms', '').split()[0] if rep.get('prenoms') else None,
                            'last_name': rep.get('nom'),
                            'role': rep.get('qualite'),
                            'linkedin': None,  # Not available from Pappers
                            'email': None,
                            'phone': None
                        }

                        if exec_data['last_name']:
                            result['executives'].append(exec_data)

                    self.stats['pappers_used'] += 1
                    return result

        except Exception as e:
            logger.debug(f"Pappers API error for {company_name}: {e}")

        return None

    def get_hunter_emails(self, domain, company_name):
        """Get emails from Hunter.io API"""
        if not self.hunter_api_key:
            return []

        try:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key,
                'limit': 5
            }

            response = self.session.get(url, params=params, timeout=15)

            # Check for quota exceeded
            if response.status_code == 429:
                logger.warning(f"{Fore.YELLOW}⚠️  Hunter API quota exceeded, continuing without API")
                self.hunter_api_key = None  # Disable for future calls
                return []

            if response.status_code == 200:
                data = response.json()

                if data.get('data', {}).get('emails'):
                    emails = []
                    for email_data in data['data']['emails']:
                        email = email_data.get('value')
                        if email:
                            emails.append({
                                'email': email,
                                'first_name': email_data.get('first_name'),
                                'last_name': email_data.get('last_name'),
                                'position': email_data.get('position'),
                                'confidence': email_data.get('confidence'),
                                'type': email_data.get('type')
                            })

                    self.stats['hunter_used'] += 1
                    if emails:
                        self.stats['emails_found'] += len(emails)

                    return emails

        except Exception as e:
            logger.debug(f"Hunter API error for {domain}: {e}")

        return []

    def enrich_single_company(self, company_name, domain):
        """Enrich a single company"""
        logger.info(f"\n{Fore.CYAN}Enriching: {company_name} ({domain})")

        result = {
            'company_name': company_name,
            'domain': domain,
            'company_email': None,
            'company_phone': None,
            'company_linkedin': None,
            'company_address': None,
            'company_city': None,
            'siren': None,
            'siret': None,
            'executives': [],
            'data_sources': []
        }

        # Strategy 1: Scrape website (always do this, it's free)
        web_data = self.scrape_contact_page(domain)

        if web_data['emails']:
            result['company_email'] = web_data['emails'][0]
            result['data_sources'].append('website')
            logger.info(f"  ✓ Email: {result['company_email']}")

        if web_data['phones']:
            result['company_phone'] = web_data['phones'][0]
            logger.info(f"  ✓ Phone: {result['company_phone']}")

        if web_data['linkedin_company']:
            result['company_linkedin'] = web_data['linkedin_company']
            logger.info(f"  ✓ LinkedIn: {result['company_linkedin']}")

        # Strategy 2: Pappers.fr (French companies only)
        pappers_data = self.get_pappers_data(company_name, domain)

        if pappers_data:
            result['siren'] = pappers_data.get('siren')
            result['siret'] = pappers_data.get('siret')
            result['company_address'] = pappers_data.get('address')
            result['company_city'] = pappers_data.get('city')
            result['executives'] = pappers_data.get('executives', [])
            result['data_sources'].append('pappers')

            logger.info(f"  ✓ Pappers: {len(result['executives'])} executives found")
            for exec in result['executives'][:2]:
                logger.info(f"    - {exec.get('first_name', '')} {exec.get('last_name', '')} ({exec.get('role', 'N/A')})")

        # Strategy 3: Hunter.io (use sparingly, only 50/month)
        # Only use if we don't have email yet
        if not result['company_email'] and self.hunter_api_key:
            hunter_emails = self.get_hunter_emails(domain, company_name)

            if hunter_emails:
                # Find generic company email
                for email_data in hunter_emails:
                    if email_data.get('type') in ['generic', 'contact']:
                        result['company_email'] = email_data['email']
                        result['data_sources'].append('hunter')
                        logger.info(f"  ✓ Hunter email: {result['company_email']}")
                        break

                # Match executives with emails
                for exec in result['executives']:
                    for email_data in hunter_emails:
                        if (email_data.get('last_name', '').lower() == exec.get('last_name', '').lower() and
                            email_data.get('first_name', '').lower() == exec.get('first_name', '').lower()):
                            exec['email'] = email_data['email']
                            logger.info(f"    - Email matched: {exec['email']}")

        # Enhance executives with LinkedIn from web scraping
        if web_data['linkedin_profiles']:
            for i, exec in enumerate(result['executives']):
                if i < len(web_data['linkedin_profiles']):
                    exec['linkedin'] = web_data['linkedin_profiles'][i]

        if not result['data_sources']:
            logger.warning(f"  ✗ No data found")

        return result

    def enrich_companies_bulk(self, companies_data, max_results=None):
        """Enrich multiple companies"""
        if max_results:
            companies_data = companies_data[:max_results]

        logger.info(f"{Fore.CYAN}{'='*60}")
        logger.info(f"{Fore.CYAN}COMPANY DATA ENRICHER - Professional Free Tier")
        logger.info(f"{Fore.CYAN}Processing {len(companies_data)} companies...")
        logger.info(f"{Fore.CYAN}{'='*60}\n")

        results = []

        for company_data in tqdm(companies_data, desc="Enriching"):
            company_name = company_data.get('company_name')
            domain = company_data.get('domain')

            if not domain:
                logger.debug(f"Skipping {company_name} - no domain")
                continue

            result = self.enrich_single_company(company_name, domain)
            results.append(result)

            time.sleep(1.5)  # Be respectful to servers

        return results

    def export_results(self, results, filename='output/company_enriched_data'):
        """Export enriched data"""
        if not results:
            logger.warning("No results to export")
            return

        # Flatten executives for CSV
        flattened = []
        for company in results:
            base_data = {
                'company_name': company['company_name'],
                'domain': company['domain'],
                'company_email': company['company_email'],
                'company_phone': company['company_phone'],
                'company_linkedin': company['company_linkedin'],
                'company_address': company['company_address'],
                'company_city': company['company_city'],
                'siren': company['siren'],
                'siret': company['siret'],
                'data_sources': ', '.join(company['data_sources'])
            }

            if company['executives']:
                for i, exec in enumerate(company['executives'], 1):
                    row = base_data.copy()
                    row.update({
                        f'executive_{i}_first_name': exec.get('first_name'),
                        f'executive_{i}_last_name': exec.get('last_name'),
                        f'executive_{i}_role': exec.get('role'),
                        f'executive_{i}_email': exec.get('email'),
                        f'executive_{i}_phone': exec.get('phone'),
                        f'executive_{i}_linkedin': exec.get('linkedin')
                    })
                    flattened.append(row)
                    break  # Only first exec for CSV simplicity
            else:
                flattened.append(base_data)

        # JSON (full data)
        with open(f'{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"{Fore.GREEN}Saved: {filename}.json")

        # CSV
        df = pd.DataFrame(flattened)
        df.to_csv(f'{filename}.csv', index=False, encoding='utf-8')
        logger.info(f"{Fore.GREEN}Saved: {filename}.csv")

        # Excel
        df.to_excel(f'{filename}.xlsx', index=False, engine='openpyxl')
        logger.info(f"{Fore.GREEN}Saved: {filename}.xlsx")

        # Statistics
        companies_with_email = sum(1 for r in results if r['company_email'])
        companies_with_phone = sum(1 for r in results if r['company_phone'])
        companies_with_linkedin = sum(1 for r in results if r['company_linkedin'])
        companies_with_executives = sum(1 for r in results if r['executives'])
        total_executives = sum(len(r['executives']) for r in results)

        logger.info(f"\n{Fore.CYAN}{'='*60}")
        logger.info(f"{Fore.CYAN}ENRICHMENT STATISTICS")
        logger.info(f"{Fore.CYAN}{'='*60}")
        logger.info(f"  Total companies processed: {len(results)}")
        logger.info(f"")
        logger.info(f"  Company Data Found:")
        logger.info(f"    • Emails: {companies_with_email} ({companies_with_email/len(results)*100:.1f}%)")
        logger.info(f"    • Phones: {companies_with_phone} ({companies_with_phone/len(results)*100:.1f}%)")
        logger.info(f"    • LinkedIn: {companies_with_linkedin} ({companies_with_linkedin/len(results)*100:.1f}%)")
        logger.info(f"")
        logger.info(f"  Executive Data:")
        logger.info(f"    • Companies with executives: {companies_with_executives} ({companies_with_executives/len(results)*100:.1f}%)")
        logger.info(f"    • Total executives found: {total_executives}")
        logger.info(f"")
        logger.info(f"  API Usage:")
        logger.info(f"    • Websites scraped: {self.stats['website_scraped']}")
        logger.info(f"    • Pappers API calls: {self.stats['pappers_used']}")
        logger.info(f"    • Hunter API calls: {self.stats['hunter_used']}")


def main():
    """Run company enricher"""

    # Load domains from previous step
    logger.info("Loading company domains...")

    # Read from CSV (company_domains_premium.csv)
    try:
        df = pd.read_csv('output/company_domains_premium.csv')

        # Filter only companies with domains
        companies_to_enrich = [
            {'company_name': row['company_name'], 'domain': row['domain']}
            for _, row in df.iterrows()
            if pd.notna(row.get('domain')) and row.get('domain')
        ]
    except FileNotFoundError:
        # Fallback to JSON if CSV not found
        with open('output/company_domains_premium.json', 'r', encoding='utf-8') as f:
            domains_data = json.load(f)

        companies_to_enrich = [
            {'company_name': item['company_name'], 'domain': item['domain']}
            for item in domains_data
            if item.get('domain')
        ]

    logger.info(f"Found {len(companies_to_enrich)} companies with domains")

    # Initialize enricher
    enricher = CompanyEnricher()

    # Check API keys
    if enricher.pappers_api_key:
        logger.info(f"{Fore.GREEN}✓ Pappers API initialized")
    else:
        logger.warning(f"{Fore.YELLOW}⚠️  No Pappers API key found. Using web scraping only.")
        logger.warning(f"{Fore.YELLOW}   Get free key at: https://www.pappers.fr/api")

    if enricher.hunter_api_key:
        logger.info(f"{Fore.GREEN}✓ Hunter API initialized")
    else:
        logger.warning(f"{Fore.YELLOW}⚠️  No Hunter API key found. Using web scraping only.")
        logger.warning(f"{Fore.YELLOW}   Get free key at: https://hunter.io/users/sign_up")

    logger.info("")

    # Start timer
    start_time = time.time()

    # Enrich ALL companies with domains
    results = enricher.enrich_companies_bulk(
        companies_to_enrich,
        max_results=None  # Process all companies
    )

    # Calculate time
    elapsed_time = time.time() - start_time

    logger.info(f"\n{Fore.GREEN}{'='*60}")
    logger.info(f"{Fore.GREEN}PERFORMANCE")
    logger.info(f"{Fore.GREEN}{'='*60}")
    logger.info(f"  Total time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} min)")
    logger.info(f"  Time per company: {elapsed_time/len(results):.1f}s")

    # Export
    enricher.export_results(results, 'output/company_enriched_data')


if __name__ == '__main__':
    main()
