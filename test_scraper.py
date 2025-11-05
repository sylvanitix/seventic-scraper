"""
Test script for the improved universal scraper
Tests on multiple real-world websites
"""

from universal_scraper import scrape_companies_from_url
import json

def test_site(url, max_pages=2, site_name=""):
    """Test scraper on a specific site"""
    print(f"\n{'='*70}")
    print(f"Testing: {site_name}")
    print(f"URL: {url}")
    print(f"Max pages: {max_pages}")
    print(f"{'='*70}\n")

    try:
        companies = scrape_companies_from_url(url, max_pages)

        print(f"\n✅ SUCCESS!")
        print(f"Found {len(companies)} companies\n")

        # Show first 20
        print("First 20 companies:")
        for i, company in enumerate(companies[:20], 1):
            print(f"  {i}. {company['name']}")

        if len(companies) > 20:
            print(f"  ... and {len(companies) - 20} more")

        # Save to file
        filename = f"test_results_{site_name.lower().replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to: {filename}")

        return True, len(companies)

    except Exception as e:
        print(f"\n❌ FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    """Run tests on multiple sites"""
    test_sites = [
        {
            'name': 'Batiment.eu (Isolation)',
            'url': 'https://batiment.eu/isolation-c13-p1.html',
            'max_pages': 2
        },
        {
            'name': 'Batiweb (Fabricants BTP)',
            'url': 'https://www.batiweb.com/fabricants-btp',
            'max_pages': 1  # Single page with all companies
        },
        {
            'name': 'Equipauto (Hubj2c)',
            'url': 'https://new-liste-exposants.hubj2c.com/',
            'max_pages': 2
        }
    ]

    results = []

    print("\n" + "="*70)
    print("UNIVERSAL SCRAPER - MULTI-SITE TEST")
    print("="*70)

    for site in test_sites:
        success, count = test_site(
            url=site['url'],
            max_pages=site['max_pages'],
            site_name=site['name']
        )

        results.append({
            'site': site['name'],
            'success': success,
            'companies_found': count
        })

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70 + "\n")

    for result in results:
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"{status} | {result['site']}: {result['companies_found']} companies")

    total_success = sum(1 for r in results if r['success'])
    total_companies = sum(r['companies_found'] for r in results)

    print(f"\nTotal: {total_success}/{len(results)} sites successful")
    print(f"Total companies found: {total_companies}")


if __name__ == '__main__':
    main()
