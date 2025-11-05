"""
Lead Generation Pipeline - Integrated Scraper + Domain Finder + Enricher
Scrape any website → Find domains → Enrich companies (all in one)

Usage:
    python3 lead_pipeline.py https://example.com/exhibitors --max-pages 5

    Or import it:
    from lead_pipeline import LeadPipeline
    pipeline = LeadPipeline()
    results = pipeline.run("https://example.com/exhibitors", max_pages=5)
"""

import json
import time
import logging
import argparse
from colorama import Fore, init
from tqdm import tqdm
import pandas as pd

# Import our existing modules
from universal_scraper import UniversalScraper
from domain_finder import PremiumDomainFinder
from company_enricher import CompanyEnricher

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LeadPipeline:
    """
    Complete lead generation pipeline

    Steps:
    1. Scrape company names from any website (with pagination)
    2. Find domains for each company
    3. Enrich with contact data (email, phone, LinkedIn, executives)
    """

    def __init__(self, pappers_api_key=None, hunter_api_key=None):
        self.scraper = None
        self.domain_finder = PremiumDomainFinder()
        self.enricher = CompanyEnricher(pappers_api_key, hunter_api_key)

        self.results = {
            'companies_scraped': [],
            'domains_found': [],
            'companies_enriched': [],
            'stats': {}
        }

    def step1_scrape_companies(self, url, max_pages=10):
        """
        Step 1: Scrape company names from website

        Args:
            url: Starting URL
            max_pages: Maximum pages to scrape

        Returns:
            List of company names
        """
        logger.info(f"\n{Fore.CYAN}{'='*70}")
        logger.info(f"{Fore.CYAN}STEP 1/3: SCRAPING COMPANY NAMES")
        logger.info(f"{Fore.CYAN}{'='*70}\n")
        logger.info(f"URL: {url}")
        logger.info(f"Max pages: {max_pages}\n")

        self.scraper = UniversalScraper(headless=True)

        try:
            company_names = self.scraper.scrape_url(url, max_pages)

            logger.info(f"\n{Fore.GREEN}✓ Found {len(company_names)} unique companies")

            self.results['companies_scraped'] = company_names
            return company_names

        finally:
            if self.scraper:
                self.scraper.close()

    def step2_find_domains(self, company_names, progress_callback=None):
        """
        Step 2: Find domains for companies

        Args:
            company_names: List of company names
            progress_callback: Optional progress callback

        Returns:
            List of domain results
        """
        logger.info(f"\n{Fore.CYAN}{'='*70}")
        logger.info(f"{Fore.CYAN}STEP 2/3: FINDING DOMAINS")
        logger.info(f"{Fore.CYAN}{'='*70}\n")
        logger.info(f"Processing {len(company_names)} companies...\n")

        results = []

        for i, company_name in enumerate(tqdm(company_names, desc="Finding domains")):
            if progress_callback:
                progress_callback(i + 1, len(company_names), f"Finding domain for: {company_name}")

            result = self.domain_finder.find_domain_single(company_name)
            results.append(result)
            time.sleep(1)  # Be respectful

        # Statistics
        found = sum(1 for r in results if r['domain'])
        high_confidence = sum(1 for r in results if r.get('confidence_score', 0) >= 0.7)

        logger.info(f"\n{Fore.GREEN}✓ Found {found}/{len(company_names)} domains ({found/len(company_names)*100:.1f}%)")
        logger.info(f"  High confidence (≥70%): {high_confidence}")

        self.results['domains_found'] = results
        return results

    def step3_enrich_companies(self, domain_results, progress_callback=None):
        """
        Step 3: Enrich companies with contact data

        Args:
            domain_results: List of domain results from step 2
            progress_callback: Optional progress callback

        Returns:
            List of enriched company data
        """
        logger.info(f"\n{Fore.CYAN}{'='*70}")
        logger.info(f"{Fore.CYAN}STEP 3/3: ENRICHING COMPANY DATA")
        logger.info(f"{Fore.CYAN}{'='*70}\n")

        # Filter companies with valid domains
        companies_with_domains = [
            {'company_name': r['company_name'], 'domain': r['domain']}
            for r in domain_results
            if r.get('domain')
        ]

        logger.info(f"Enriching {len(companies_with_domains)} companies with domains...\n")

        if not companies_with_domains:
            logger.warning(f"{Fore.YELLOW}No companies with domains to enrich")
            return []

        results = []

        for i, company_data in enumerate(tqdm(companies_with_domains, desc="Enriching")):
            if progress_callback:
                progress_callback(i + 1, len(companies_with_domains),
                                f"Enriching: {company_data['company_name']}")

            result = self.enricher.enrich_single_company(
                company_data['company_name'],
                company_data['domain']
            )
            results.append(result)
            time.sleep(1.5)  # Be respectful

        # Statistics
        with_email = sum(1 for r in results if r.get('company_email'))
        with_phone = sum(1 for r in results if r.get('company_phone'))
        with_linkedin = sum(1 for r in results if r.get('company_linkedin'))

        logger.info(f"\n{Fore.GREEN}✓ Enriched {len(results)} companies")
        logger.info(f"  With email: {with_email} ({with_email/len(results)*100:.1f}%)")
        logger.info(f"  With phone: {with_phone} ({with_phone/len(results)*100:.1f}%)")
        logger.info(f"  With LinkedIn: {with_linkedin} ({with_linkedin/len(results)*100:.1f}%)")

        self.results['companies_enriched'] = results
        return results

    def run(self, url, max_pages=10, export_csv=True, output_prefix='output/leads',
            progress_callback=None):
        """
        Run complete pipeline

        Args:
            url: Starting URL to scrape
            max_pages: Maximum pages to scrape
            export_csv: Export results to CSV/Excel
            output_prefix: Output file prefix
            progress_callback: Optional progress callback

        Returns:
            Dictionary with all results
        """
        start_time = time.time()

        logger.info(f"{Fore.CYAN}{'='*70}")
        logger.info(f"{Fore.CYAN}LEAD GENERATION PIPELINE")
        logger.info(f"{Fore.CYAN}{'='*70}\n")

        # Step 1: Scrape company names
        company_names = self.step1_scrape_companies(url, max_pages)

        if not company_names:
            logger.error(f"{Fore.RED}No companies found. Exiting.")
            return None

        # Step 2: Find domains
        domain_results = self.step2_find_domains(company_names, progress_callback)

        # Step 3: Enrich companies
        enriched_results = self.step3_enrich_companies(domain_results, progress_callback)

        # Calculate final stats
        elapsed_time = time.time() - start_time

        self.results['stats'] = {
            'total_companies_scraped': len(company_names),
            'domains_found': sum(1 for r in domain_results if r.get('domain')),
            'companies_enriched': len(enriched_results),
            'emails_found': sum(1 for r in enriched_results if r.get('company_email')),
            'phones_found': sum(1 for r in enriched_results if r.get('company_phone')),
            'linkedin_found': sum(1 for r in enriched_results if r.get('company_linkedin')),
            'total_time_seconds': elapsed_time,
            'time_per_company': elapsed_time / len(company_names) if company_names else 0
        }

        # Display final summary
        self._print_summary()

        # Export if requested
        if export_csv:
            self.export_results(output_prefix)

        return self.results

    def _print_summary(self):
        """Print final summary"""
        stats = self.results['stats']

        logger.info(f"\n{Fore.GREEN}{'='*70}")
        logger.info(f"{Fore.GREEN}PIPELINE COMPLETE - FINAL SUMMARY")
        logger.info(f"{Fore.GREEN}{'='*70}\n")

        logger.info(f"Companies scraped:     {stats['total_companies_scraped']}")
        logger.info(f"Domains found:         {stats['domains_found']} ({stats['domains_found']/stats['total_companies_scraped']*100:.1f}%)")
        logger.info(f"Companies enriched:    {stats['companies_enriched']}")
        logger.info(f"")
        logger.info(f"Contact data found:")
        logger.info(f"  • Emails:    {stats['emails_found']} ({stats['emails_found']/stats['companies_enriched']*100:.1f}% of enriched)" if stats['companies_enriched'] else "  • Emails:    0")
        logger.info(f"  • Phones:    {stats['phones_found']} ({stats['phones_found']/stats['companies_enriched']*100:.1f}% of enriched)" if stats['companies_enriched'] else "  • Phones:    0")
        logger.info(f"  • LinkedIn:  {stats['linkedin_found']} ({stats['linkedin_found']/stats['companies_enriched']*100:.1f}% of enriched)" if stats['companies_enriched'] else "  • LinkedIn:  0")
        logger.info(f"")
        logger.info(f"Total time:            {stats['total_time_seconds']:.1f}s ({stats['total_time_seconds']/60:.1f} min)")
        logger.info(f"Time per company:      {stats['time_per_company']:.1f}s")
        logger.info(f"")

    def export_results(self, output_prefix='output/leads'):
        """
        Export results to CSV, Excel, and JSON

        Args:
            output_prefix: Output file prefix (without extension)
        """
        if not self.results['companies_enriched']:
            logger.warning(f"{Fore.YELLOW}No enriched data to export")
            return

        logger.info(f"\n{Fore.CYAN}Exporting results...")

        # Prepare data for export
        export_data = []

        for company in self.results['companies_enriched']:
            row = {
                'company_name': company['company_name'],
                'domain': company['domain'],
                'email': company.get('company_email'),
                'phone': company.get('company_phone'),
                'linkedin': company.get('company_linkedin'),
                'address': company.get('company_address'),
                'city': company.get('company_city'),
                'siren': company.get('siren'),
                'siret': company.get('siret'),
                'data_sources': ', '.join(company.get('data_sources', []))
            }

            # Add first executive if available
            if company.get('executives'):
                exec = company['executives'][0]
                row.update({
                    'executive_first_name': exec.get('first_name'),
                    'executive_last_name': exec.get('last_name'),
                    'executive_role': exec.get('role'),
                    'executive_email': exec.get('email'),
                    'executive_linkedin': exec.get('linkedin')
                })

            export_data.append(row)

        # Export to CSV
        df = pd.DataFrame(export_data)
        csv_path = f'{output_prefix}.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"{Fore.GREEN}✓ Saved: {csv_path}")

        # Export to Excel
        excel_path = f'{output_prefix}.xlsx'
        df.to_excel(excel_path, index=False, engine='openpyxl')
        logger.info(f"{Fore.GREEN}✓ Saved: {excel_path}")

        # Export full JSON (with all data)
        json_path = f'{output_prefix}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logger.info(f"{Fore.GREEN}✓ Saved: {json_path}")

        logger.info(f"\n{Fore.GREEN}All results exported successfully!")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description='Lead Generation Pipeline - Scrape, Find Domains, and Enrich Companies'
    )
    parser.add_argument('url', help='Starting URL to scrape')
    parser.add_argument('--max-pages', type=int, default=10,
                       help='Maximum pages to scrape (default: 10)')
    parser.add_argument('--output', default='output/leads',
                       help='Output file prefix (default: output/leads)')
    parser.add_argument('--no-export', action='store_true',
                       help='Skip CSV/Excel export')

    args = parser.parse_args()

    # Run pipeline
    pipeline = LeadPipeline()
    results = pipeline.run(
        url=args.url,
        max_pages=args.max_pages,
        export_csv=not args.no_export,
        output_prefix=args.output
    )

    if results:
        logger.info(f"\n{Fore.GREEN}{'='*70}")
        logger.info(f"{Fore.GREEN}SUCCESS! Check your output files:")
        logger.info(f"{Fore.GREEN}{'='*70}")
        logger.info(f"  • {args.output}.csv")
        logger.info(f"  • {args.output}.xlsx")
        logger.info(f"  • {args.output}.json")


if __name__ == '__main__':
    main()
