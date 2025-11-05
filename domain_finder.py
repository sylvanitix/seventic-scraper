"""
Premium Domain Finder - Using best available free APIs
Focus: Maximum quality and accuracy
"""
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from colorama import Fore, init
from tqdm import tqdm
import re
from urllib.parse import urlparse

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PremiumDomainFinder:
    """Premium domain finder using multiple reliable sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.results = []

        # Parking indicators
        self.parking_keywords = [
            'domain is for sale', 'buy this domain', 'domain parking',
            'parked domain', 'expired domain', 'premium domain',
            'make an offer', 'domain broker', 'sedo', 'godaddy parking'
        ]

    def clean_company_name(self, name):
        """Clean company name"""
        suffixes = ['ltd', 'limited', 'inc', 'incorporated', 'corp', 'corporation',
                   'gmbh', 'sa', 'sas', 'sarl', 'srl', 'spa', 's.r.l.', 's.p.a.',
                   'b.v.', 'bv', 'co', 'cie', 'france']

        name_lower = name.lower()
        for suffix in suffixes:
            name_lower = re.sub(rf'\b{suffix}\b', '', name_lower)

        name_clean = re.sub(r'[^a-z0-9\s]', ' ', name_lower)
        name_clean = re.sub(r'\s+', ' ', name_clean).strip()

        return name_clean

    def search_clearbit_logo(self, company_name):
        """Use Clearbit Logo API (free, no key needed)"""
        try:
            clean_name = self.clean_company_name(company_name)
            clean_name = clean_name.replace(' ', '')

            # Try .com first
            for tld in ['.com', '.fr', '.net']:
                domain = f"{clean_name}{tld}"
                url = f"https://logo.clearbit.com/{domain}"

                try:
                    response = self.session.head(url, timeout=5)
                    if response.status_code == 200:
                        return domain
                except:
                    continue

        except Exception as e:
            logger.debug(f"Clearbit error for {company_name}: {e}")

        return None

    def search_company_website_api(self, company_name):
        """
        Use autocomplete.clearbit.com (free API, no key needed)
        This is their company autocomplete API
        """
        try:
            query = company_name
            url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={requests.utils.quote(query)}"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                results = response.json()

                if results and len(results) > 0:
                    # First result is usually the best match
                    first_result = results[0]
                    domain = first_result.get('domain')

                    if domain:
                        logger.debug(f"Clearbit API found: {domain} for {company_name}")
                        return domain, first_result.get('name'), first_result.get('logo')

        except Exception as e:
            logger.debug(f"Clearbit API error for {company_name}: {e}")

        return None, None, None

    def verify_domain_content(self, domain, company_name):
        """
        Verify domain is real company website, not parked

        Returns: (is_valid, confidence, reason)
        """
        try:
            url = f"https://{domain}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code >= 400:
                return False, 0.0, "Site not accessible"

            # Check redirect to parking
            final_url = response.url
            parking_domains = ['sedo.com', 'godaddy.com', 'namecheap.com',
                             'afternic.com', 'dan.com', 'parkingcrew']

            for parking_domain in parking_domains:
                if parking_domain in final_url:
                    return False, 0.0, f"Redirects to parking: {parking_domain}"

            # Check content
            soup = BeautifulSoup(response.text, 'lxml')
            text_content = soup.get_text().lower()

            # Check for parking keywords
            parking_count = sum(1 for keyword in self.parking_keywords
                              if keyword in text_content)

            if parking_count >= 2:
                return False, 0.0, f"Contains {parking_count} parking keywords"

            # Check for minimal content
            if len(text_content.strip()) < 200:
                return False, 0.3, "Very minimal content"

            # Check for company name match
            company_clean = self.clean_company_name(company_name).lower()
            company_words = [w for w in company_clean.split() if len(w) > 3]

            # Check title
            title = soup.find('title')
            if title:
                title_text = title.get_text().lower()
                words_in_title = sum(1 for word in company_words if word in title_text)

                if words_in_title >= min(2, len(company_words)):
                    return True, 0.9, "Company name in title"

            # Check headings
            headings = soup.find_all(['h1', 'h2'])
            for heading in headings:
                heading_text = heading.get_text().lower()
                words_in_heading = sum(1 for word in company_words if word in heading_text)

                if words_in_heading >= 2:
                    return True, 0.7, "Company name in headings"

            # Check general content match
            if company_words:
                words_in_content = sum(1 for word in company_words if word in text_content)
                match_ratio = words_in_content / len(company_words)

                if match_ratio >= 0.5:
                    return True, 0.6, f"Company keywords match ({match_ratio:.0%})"

            # Has real content but no clear company match
            return False, 0.4, "Content doesn't match company"

        except Exception as e:
            logger.debug(f"Validation error for {domain}: {e}")
            return None, 0.0, f"Error: {str(e)}"

    def calculate_confidence_score(self, confidence, clearbit_name, company_name, method):
        """
        Calculate overall confidence score and estimated false positive rate

        Returns: (confidence_score, false_positive_rate, confidence_label)
        """
        # Base confidence from content validation
        score = confidence

        # Adjust based on Clearbit name match
        if clearbit_name:
            company_clean = self.clean_company_name(company_name).lower()
            clearbit_clean = self.clean_company_name(clearbit_name).lower()

            # Exact match boost
            if company_clean == clearbit_clean:
                score += 0.1
            # Similar match
            elif any(word in clearbit_clean for word in company_clean.split() if len(word) > 3):
                score += 0.05
            # No match - penalty
            else:
                score -= 0.2

        # Cap at 1.0
        score = min(1.0, max(0.0, score))

        # Calculate false positive rate based on score
        if score >= 0.9:
            fp_rate = 0.05  # 5% false positive
            label = "Très élevée - Très fiable"
        elif score >= 0.7:
            fp_rate = 0.15  # 15% false positive
            label = "Élevée - Fiable"
        elif score >= 0.5:
            fp_rate = 0.40  # 40% false positive
            label = "Moyenne - À vérifier"
        else:
            fp_rate = 0.70  # 70% false positive
            label = "Faible - Douteux"

        return score, fp_rate, label

    def find_domain_single(self, company_name):
        """Find and validate domain for a single company"""
        result = {
            'company_name': company_name,
            'domain': None,
            'confidence_score': 0.0,
            'confidence_label': 'Non trouvé',
            'false_positive_rate': 1.0,
            'method': 'not_found',
            'validation_reason': None,
            'clearbit_name': None
        }

        logger.info(f"\n{Fore.CYAN}Searching: {company_name}")

        # Strategy 1: Clearbit Autocomplete API (best method, free)
        domain, clearbit_name, logo = self.search_company_website_api(company_name)

        if domain:
            logger.info(f"  Found via Clearbit API: {domain}")

            if clearbit_name:
                result['clearbit_name'] = clearbit_name
                logger.info(f"  Clearbit name: {clearbit_name}")

            # Validate it's not parked and matches company
            is_valid, confidence, reason = self.verify_domain_content(domain, company_name)

            if is_valid and confidence >= 0.5:
                # Calculate final confidence score
                conf_score, fp_rate, conf_label = self.calculate_confidence_score(
                    confidence, clearbit_name, company_name, 'clearbit_api'
                )

                result['domain'] = domain
                result['confidence_score'] = conf_score
                result['confidence_label'] = conf_label
                result['false_positive_rate'] = fp_rate
                result['method'] = 'clearbit_api+validated'
                result['validation_reason'] = reason
                logger.info(f"  {Fore.GREEN}✓ VALIDATED: {domain}")
                logger.info(f"    Score: {conf_score:.0%} ({conf_label})")
                logger.info(f"    Faux positif estimé: {fp_rate:.0%}")
                return result
            else:
                logger.warning(f"  {Fore.YELLOW}✗ Rejected: {reason}")

        # Strategy 2: Clearbit Logo API fallback
        time.sleep(0.5)
        domain = self.search_clearbit_logo(company_name)

        if domain:
            logger.info(f"  Found via Clearbit Logo: {domain}")

            is_valid, confidence, reason = self.verify_domain_content(domain, company_name)

            if is_valid and confidence >= 0.5:
                # Calculate final confidence score
                conf_score, fp_rate, conf_label = self.calculate_confidence_score(
                    confidence, None, company_name, 'clearbit_logo'
                )

                result['domain'] = domain
                result['confidence_score'] = conf_score
                result['confidence_label'] = conf_label
                result['false_positive_rate'] = fp_rate
                result['method'] = 'clearbit_logo+validated'
                result['validation_reason'] = reason
                logger.info(f"  {Fore.GREEN}✓ VALIDATED: {domain}")
                logger.info(f"    Score: {conf_score:.0%} ({conf_label})")
                logger.info(f"    Faux positif estimé: {fp_rate:.0%}")
                return result

        # Nothing found
        logger.warning(f"  {Fore.YELLOW}✗ No valid domain found")
        return result

    def find_domains_bulk(self, companies, max_results=None):
        """Find domains for multiple companies"""
        if max_results:
            companies = companies[:max_results]

        logger.info(f"{Fore.CYAN}{'='*60}")
        logger.info(f"{Fore.CYAN}PREMIUM QUALITY MODE - Accuracy over Speed")
        logger.info(f"{Fore.CYAN}Processing {len(companies)} companies...")
        logger.info(f"{Fore.CYAN}{'='*60}\n")

        results = []

        for company in tqdm(companies, desc="Processing"):
            result = self.find_domain_single(company)
            results.append(result)
            time.sleep(1)  # Be respectful to APIs

        self.results = results
        return results

    def export_results(self, filename='output/domains_premium'):
        """Export results"""
        if not self.results:
            logger.warning("No results to export")
            return

        # JSON
        with open(f'{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logger.info(f"{Fore.GREEN}Saved: {filename}.json")

        # CSV
        df = pd.DataFrame(self.results)
        df.to_csv(f'{filename}.csv', index=False, encoding='utf-8')
        logger.info(f"{Fore.GREEN}Saved: {filename}.csv")

        # Excel
        df.to_excel(f'{filename}.xlsx', index=False, engine='openpyxl')
        logger.info(f"{Fore.GREEN}Saved: {filename}.xlsx")

        # Statistics
        found = sum(1 for r in self.results if r['domain'])
        very_high = sum(1 for r in self.results if r.get('confidence_score', 0) >= 0.9)
        high_conf = sum(1 for r in self.results if 0.7 <= r.get('confidence_score', 0) < 0.9)
        medium_conf = sum(1 for r in self.results if 0.5 <= r.get('confidence_score', 0) < 0.7)

        logger.info(f"\n{Fore.CYAN}{'='*60}")
        logger.info(f"{Fore.CYAN}STATISTIQUES DE QUALITÉ")
        logger.info(f"{Fore.CYAN}{'='*60}")
        logger.info(f"  Total entreprises: {len(self.results)}")
        logger.info(f"  Domaines trouvés: {found} ({found/len(self.results)*100:.1f}%)")
        logger.info(f"")
        logger.info(f"  Par niveau de confiance:")
        logger.info(f"    • Très élevée (≥90%): {very_high} - Faux positif ~5%")
        logger.info(f"    • Élevée (70-90%): {high_conf} - Faux positif ~15%")
        logger.info(f"    • Moyenne (50-70%): {medium_conf} - Faux positif ~40%")
        logger.info(f"")
        logger.info(f"  Non trouvés: {len(self.results) - found}")
        logger.info(f"\n{Fore.YELLOW}⚠️  Validation manuelle recommandée pour confiance < 90%")


def main():
    """Run premium domain finder"""

    # Load companies
    logger.info(f"Loading company names...")
    with open('output/equipauto_exhibitors_clean.json', 'r', encoding='utf-8') as f:
        exhibitors = json.load(f)

    company_names = [ex['name'] for ex in exhibitors]

    # Initialize finder
    finder = PremiumDomainFinder()

    # Start timer
    start_time = time.time()

    # Find domains (test on 50, then change to None for all)
    results = finder.find_domains_bulk(
        company_names,
        max_results=50  # Change to None for all 1301
    )

    # Calculate time
    elapsed_time = time.time() - start_time

    logger.info(f"\n{Fore.GREEN}{'='*60}")
    logger.info(f"{Fore.GREEN}PERFORMANCE")
    logger.info(f"{Fore.GREEN}{'='*60}")
    logger.info(f"  Total time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} min)")
    logger.info(f"  Time per company: {elapsed_time/len(results):.1f}s")

    # Export
    finder.export_results('output/company_domains_premium')

    # Show validated results by confidence level
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}DOMAINES VALIDÉS")
    print(f"{Fore.CYAN}{'='*60}\n")

    # Sort by confidence score
    found_results = [r for r in results if r['domain']]
    found_results.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)

    for result in found_results:
        score = result.get('confidence_score', 0)
        label = result.get('confidence_label', 'N/A')
        fp_rate = result.get('false_positive_rate', 0)

        # Color based on confidence
        if score >= 0.9:
            color = Fore.GREEN
        elif score >= 0.7:
            color = Fore.CYAN
        else:
            color = Fore.YELLOW

        print(f"{color}✓ {result['company_name']}")
        print(f"  Domaine: {result['domain']}")
        print(f"  Confiance: {score:.0%} - {label}")
        print(f"  Faux positif estimé: {fp_rate:.0%}")
        if result.get('clearbit_name'):
            print(f"  Clearbit: {result['clearbit_name']}")
        print()

    # Show not found
    not_found = [r for r in results if not r['domain']]
    if not_found:
        print(f"\n{Fore.YELLOW}NON TROUVÉS ({len(not_found)}):")
        for r in not_found[:10]:  # Show first 10
            print(f"  ✗ {r['company_name']}")


if __name__ == '__main__':
    main()
