"""
Smart Pattern Detector - Like EasyScraper
Détecte automatiquement les patterns répétitifs sur une page
"""

from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import time
import re


class SmartPatternDetector:
    """
    Détecte automatiquement les structures de données répétitives sur une page web
    Similaire à EasyScraper ou Instant Data Scraper
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def get_element_signature(self, element):
        """
        Crée une signature unique pour un élément basée sur sa structure
        """
        tag = element.name
        classes = ' '.join(sorted(element.get('class', [])))

        # Signature = tag + classes principales
        signature = f"{tag}"
        if classes:
            # Garde seulement les 2 premières classes pour éviter trop de variations
            main_classes = ' '.join(classes.split()[:2])
            signature += f".{main_classes}"

        return signature

    def extract_element_data(self, element):
        """
        Extrait toutes les données intéressantes d'un élément
        """
        data = {}

        # Texte principal
        text = element.get_text(strip=True)
        if text and len(text) > 0 and len(text) < 500:
            data['text'] = text

        # Lien
        link = element.find('a')
        if link and link.get('href'):
            data['link'] = link.get('href')
            # Texte du lien si différent
            link_text = link.get_text(strip=True)
            if link_text and link_text != text:
                data['link_text'] = link_text

        # Image
        img = element.find('img')
        if img:
            if img.get('src'):
                data['image'] = img.get('src')
            if img.get('alt'):
                data['image_alt'] = img.get('alt')

        # Attributs data-*
        for attr, value in element.attrs.items():
            if attr.startswith('data-') and isinstance(value, str):
                data[attr] = value

        # Cherche des sous-éléments avec des classes spécifiques
        for child in element.find_all(['span', 'div', 'p', 'h1', 'h2', 'h3', 'h4', 'strong'], limit=20):
            child_text = child.get_text(strip=True)
            child_class_list = child.get('class') or []
            child_classes = ' '.join(child_class_list) if child_class_list else ''

            if child_text and child_text != text and len(child_text) > 2:
                # Crée une clé basée sur la classe ou le tag
                if child_classes:
                    key = f"field_{child_classes.split()[0]}"
                else:
                    key = f"field_{child.name}"

                # Évite les doublons
                if key not in data:
                    data[key] = child_text

        return data

    def find_repeating_patterns(self, html):
        """
        Trouve les patterns qui se répètent sur la page
        Retourne les patterns avec leurs données
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Groupe les éléments par signature
        elements_by_signature = defaultdict(list)

        # Cherche dans tous les conteneurs possibles
        for element in soup.find_all(['div', 'article', 'li', 'tr', 'section']):
            # Ignore les éléments trop petits ou trop grands
            text = element.get_text(strip=True)
            if not text or len(text) < 5 or len(text) > 2000:
                continue

            # Ignore les éléments trop imbriqués (probablement pas des items)
            depth = len(list(element.parents))
            if depth > 15:
                continue

            signature = self.get_element_signature(element)
            elements_by_signature[signature].append(element)

        # Trouve les patterns qui se répètent au moins 3 fois
        patterns = []
        for signature, elements in elements_by_signature.items():
            if len(elements) >= 3:  # Au moins 3 répétitions
                # Extrait les données de chaque élément
                items = []
                for elem in elements[:50]:  # Max 50 pour l'aperçu
                    data = self.extract_element_data(elem)
                    if data:  # Seulement si on a extrait des données
                        items.append(data)

                if items:
                    patterns.append({
                        'signature': signature,
                        'count': len(elements),
                        'items': items,
                        'sample_count': len(items)
                    })

        # Trie par nombre d'occurrences (plus probable = le bon pattern)
        patterns.sort(key=lambda x: x['count'], reverse=True)

        return patterns

    def detect_columns(self, pattern):
        """
        Analyse un pattern et détecte les colonnes de données
        """
        if not pattern or not pattern.get('items'):
            return []

        # Compte les champs présents dans les items
        field_counts = defaultdict(int)
        field_samples = defaultdict(list)

        for item in pattern['items']:
            for field, value in item.items():
                field_counts[field] += 1
                if len(field_samples[field]) < 5:
                    field_samples[field].append(value)

        # Crée les colonnes
        columns = []
        for field, count in field_counts.items():
            # Calcule le pourcentage de présence
            presence = (count / len(pattern['items'])) * 100

            # Détermine le type de colonne
            col_type = self.guess_column_type(field, field_samples[field])

            columns.append({
                'name': field,
                'type': col_type,
                'presence': presence,
                'samples': field_samples[field][:3]  # 3 exemples
            })

        # Trie : les colonnes avec texte en premier, puis par présence
        columns.sort(key=lambda x: (x['type'] != 'text', -x['presence']))

        return columns

    def guess_column_type(self, field_name, samples):
        """
        Devine le type de colonne basé sur le nom et les exemples
        """
        field_lower = field_name.lower()

        # Type basé sur le nom du champ
        if 'link' in field_lower or 'url' in field_lower or 'href' in field_lower:
            return 'url'
        elif 'image' in field_lower or 'img' in field_lower or 'photo' in field_lower:
            return 'image'
        elif 'text' in field_lower or 'name' in field_lower or 'title' in field_lower:
            return 'text'

        # Type basé sur le contenu
        if samples:
            first_sample = str(samples[0])
            if first_sample.startswith('http'):
                return 'url'
            elif any(ext in first_sample.lower() for ext in ['.jpg', '.png', '.gif', '.webp']):
                return 'image'

        return 'text'

    def analyze_url(self, url):
        """
        Analyse une URL et retourne les patterns détectés avec leurs colonnes
        """
        try:
            print(f"🔍 Analyse de {url}...")

            # Récupère le HTML avec requests
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            html = response.text

            # Détecte les patterns
            patterns = self.find_repeating_patterns(html)

            if not patterns:
                return {
                    'success': False,
                    'error': 'Aucun pattern répétitif détecté'
                }

            # Analyse les colonnes pour chaque pattern
            results = []
            for pattern in patterns[:5]:  # Top 5 patterns
                columns = self.detect_columns(pattern)

                results.append({
                    'signature': pattern['signature'],
                    'count': pattern['count'],
                    'columns': columns,
                    'preview': pattern['items'][:10]  # 10 premiers items
                })

            return {
                'success': True,
                'url': url,
                'patterns': results,
                'best_pattern': results[0] if results else None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def scrape_with_mapping(self, url, pattern_signature=None, pattern_index=0, company_name_column='text', max_pages=5, logger=None):
        """
        Scrape avec un mapping défini par l'utilisateur

        Args:
            url: URL à scraper
            pattern_signature: Signature du pattern (ex: "li.col-12 col-lg-4") - RECOMMANDÉ
            pattern_index: Index du pattern choisi (0 = meilleur) - utilisé si signature absente
            company_name_column: Nom de la colonne contenant les noms d'entreprises
            max_pages: Nombre max de pages à scraper
            logger: Optional function to log messages
        """
        def log(message):
            print(message)
            if logger:
                logger(message)

        try:
            log(f"🚀 Début du scraping...")
            if pattern_signature:
                log(f"🎯 Recherche du pattern: {pattern_signature}")
            else:
                log(f"🎯 Utilisation de l'index: {pattern_index}")

            all_companies = []
            visited_urls = set()
            urls_to_visit = [url]

            while urls_to_visit and len(visited_urls) < max_pages:
                current_url = urls_to_visit.pop(0)

                if current_url in visited_urls:
                    continue

                visited_urls.add(current_url)
                log(f"📄 Page {len(visited_urls)}/{max_pages}: {current_url}")

                # Récupère le HTML avec requests
                response = self.session.get(current_url, timeout=15)
                response.raise_for_status()
                html = response.text
                log(f"   HTML chargé: {len(html)} caractères")

                # Détecte les patterns
                patterns = self.find_repeating_patterns(html)
                log(f"   Patterns détectés: {len(patterns) if patterns else 0}")

                if not patterns:
                    log(f"⚠️  Aucun pattern trouvé sur {current_url}")
                    continue

                # Trouve le pattern à utiliser
                pattern = None
                if pattern_signature:
                    # Cherche par signature
                    for p in patterns:
                        if p['signature'] == pattern_signature:
                            pattern = p
                            log(f"   ✓ Pattern trouvé par signature: {pattern_signature} - {len(p['items'])} items")
                            break

                    if not pattern:
                        log(f"⚠️  Pattern '{pattern_signature}' non trouvé sur cette page")
                        log(f"   Patterns disponibles: {[p['signature'] for p in patterns[:5]]}")
                        continue
                else:
                    # Utilise l'index
                    if pattern_index >= len(patterns):
                        log(f"⚠️  Pattern index {pattern_index} invalide (max: {len(patterns)-1})")
                        continue
                    pattern = patterns[pattern_index]
                    log(f"   Pattern #{pattern_index}: {pattern['signature']} - {len(pattern['items'])} items")

                # Extrait les noms d'entreprises
                extracted_count = 0
                for item in pattern['items']:
                    if company_name_column in item:
                        company_name = item[company_name_column]

                        # Nettoyage basique
                        company_name = company_name.strip()

                        if company_name and len(company_name) > 2:
                            # Simplifié : on ne garde QUE le nom et optionnellement le lien
                            company_data = {'name': company_name}
                            if 'link' in item and item['link']:
                                company_data['url'] = item['link']

                            all_companies.append(company_data)
                            extracted_count += 1
                    else:
                        # Debug: la colonne n'existe pas dans cet item
                        if len(all_companies) < 3:  # Log seulement pour les premiers
                            log(f"   ⚠️ Colonne '{company_name_column}' absente. Colonnes disponibles: {list(item.keys())}")

                log(f"   ✓ {extracted_count} noms extraits de cette page")
                log(f"   📊 Total accumulé: {len(all_companies)} entreprises")

                # Trouve la page suivante
                if len(visited_urls) < max_pages:
                    next_urls = self.find_next_page_urls(current_url, html)
                    log(f"   🔗 Pages suivantes trouvées: {len(next_urls)}")
                    for next_url in next_urls:
                        if next_url not in visited_urls and next_url not in urls_to_visit:
                            urls_to_visit.append(next_url)
                            log(f"   → Ajout dans la queue: {next_url}")
                            break  # Une seule page suivante à la fois

            log(f"\n📊 Scraping terminé: {len(all_companies)} entreprises avant déduplication")

            # Déduplique
            seen = set()
            unique_companies = []
            for company in all_companies:
                if company['name'] not in seen:
                    seen.add(company['name'])
                    unique_companies.append(company)

            log(f"✅ Après déduplication: {len(unique_companies)} entreprises uniques")

            return unique_companies

        except Exception as e:
            log(f"❌ Erreur pendant le scraping: {str(e)}")
            import traceback
            log(traceback.format_exc())
            return []

    def find_next_page_urls(self, current_url, html):
        """
        Trouve les URLs de pagination
        """
        soup = BeautifulSoup(html, 'html.parser')
        next_urls = []

        # Cherche les liens de pagination
        pagination_patterns = [
            r'page[=/-](\d+)',
            r'p(\d+)',
            r'/(\d+)/?$'
        ]

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True).lower()

            # Liens "suivant" / "next"
            if any(word in text for word in ['suivant', 'next', '>', '»', 'suiv']):
                full_url = self.make_absolute_url(current_url, href)
                if full_url:
                    next_urls.append(full_url)

            # Liens avec numéros de page
            for pattern in pagination_patterns:
                if re.search(pattern, href):
                    full_url = self.make_absolute_url(current_url, href)
                    if full_url and full_url != current_url:
                        next_urls.append(full_url)

        # Pattern-based URL increment
        for pattern, template in [
            (r'-p(\d+)\.html', '-p{}.html'),
            (r'/page/(\d+)', '/page/{}'),
            (r'[?&]page=(\d+)', '?page={}'),
        ]:
            match = re.search(pattern, current_url)
            if match:
                current_page = int(match.group(1))
                next_url = re.sub(pattern, template.format(current_page + 1), current_url)
                next_urls.append(next_url)

        return next_urls

    def make_absolute_url(self, base_url, href):
        """Convertit une URL relative en absolue"""
        if not href:
            return None

        if href.startswith('http'):
            return href

        from urllib.parse import urljoin
        return urljoin(base_url, href)


if __name__ == '__main__':
    # Test
    detector = SmartPatternDetector()

    test_url = 'https://www.batiweb.com/fabricants-btp'

    print("="*60)
    print("TEST: Analyse automatique des patterns")
    print("="*60)

    result = detector.analyze_url(test_url)

    if result['success']:
        print(f"\n✅ {len(result['patterns'])} pattern(s) détecté(s)\n")

        for i, pattern in enumerate(result['patterns']):
            print(f"\n{'='*60}")
            print(f"PATTERN #{i+1}: {pattern['signature']}")
            print(f"{'='*60}")
            print(f"Répétitions: {pattern['count']} fois")
            print(f"\nColonnes détectées ({len(pattern['columns'])}):")

            for col in pattern['columns']:
                print(f"\n  📊 {col['name']}")
                print(f"     Type: {col['type']}")
                print(f"     Présence: {col['presence']:.1f}%")
                print(f"     Exemples: {col['samples'][:2]}")

            print(f"\n  Aperçu des données (3 premiers items):")
            for j, item in enumerate(pattern['preview'][:3], 1):
                print(f"\n  Item {j}:")
                for key, value in list(item.items())[:3]:
                    print(f"    - {key}: {value[:80] if isinstance(value, str) else value}")
    else:
        print(f"\n❌ Erreur: {result['error']}")
