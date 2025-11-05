"""
Test du scraping supervisé en local
"""

from smart_pattern_detector import SmartPatternDetector

def test_scraping():
    detector = SmartPatternDetector()

    url = 'https://www.batiweb.com/fabricants-btp'

    print("="*60)
    print("TEST 1: Analyse du site")
    print("="*60)

    # Étape 1: Analyser
    result = detector.analyze_url(url)

    if not result['success']:
        print(f"❌ Échec de l'analyse: {result['error']}")
        return

    print(f"✅ {len(result['patterns'])} patterns détectés\n")

    # Afficher le meilleur pattern
    best_pattern = result['patterns'][0]
    print(f"Meilleur pattern: {best_pattern['signature']}")
    print(f"Nombre d'items: {best_pattern['count']}")
    print(f"Colonnes disponibles:")
    for col in best_pattern['columns']:
        print(f"  - {col['name']} ({col['type']}) - {col['presence']:.1f}%")

    print("\n" + "="*60)
    print("TEST 2: Scraping avec mapping")
    print("="*60)

    # Étape 2: Scraper avec mapping
    companies = detector.scrape_with_mapping(
        url=url,
        pattern_index=0,  # Premier pattern
        company_name_column='text',  # Colonne avec les noms
        max_pages=1  # Juste 1 page pour le test
    )

    print(f"\n✅ Résultat: {len(companies)} entreprises")

    if companies:
        print("\nPremiers résultats:")
        for i, company in enumerate(companies[:10], 1):
            print(f"  {i}. {company['name']}")
            if 'url' in company:
                print(f"     → {company['url']}")
    else:
        print("❌ Aucune entreprise trouvée!")

    print("\n" + "="*60)


if __name__ == '__main__':
    test_scraping()
