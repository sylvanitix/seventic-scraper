#!/usr/bin/env python3
"""
Script pour trouver les domaines manquants dans Sales - Territoires.xlsx
Utilise la recherche Google (sans API) pour trouver les sites web
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse, quote_plus

class FreeDomainFinder:
    """Trouve des domaines avec recherche Google gratuite"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def find_domain(self, company_name):
        """Trouve le domaine d'une entreprise via Google"""
        if not company_name or pd.isna(company_name):
            return ''
        
        try:
            # Recherche Google
            query = f"{company_name} site officiel"
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cherche les URLs dans les résultats
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Extrait l'URL du résultat Google
                if '/url?q=' in href:
                    url_match = re.search(r'/url\?q=([^&]+)', href)
                    if url_match:
                        result_url = url_match.group(1)
                        
                        # Parse le domaine
                        try:
                            parsed = urlparse(result_url)
                            domain = parsed.netloc
                            
                            # Ignore les domaines connus non pertinents
                            ignore_domains = ['google', 'facebook', 'linkedin', 'twitter', 
                                            'youtube', 'wikipedia', 'societe.com', 'verif.com']
                            
                            if domain and not any(ignore in domain.lower() for ignore in ignore_domains):
                                print(f"  ✓ Trouvé: {domain}")
                                return domain
                        except:
                            continue
            
            print(f"  ✗ Pas trouvé")
            return ''
            
        except Exception as e:
            print(f"  ✗ Erreur: {str(e)}")
            return ''

def process_excel_file(input_file, output_file):
    """Traite le fichier Excel et trouve les domaines manquants"""
    
    print(f"\n📂 Lecture de {input_file}...")
    excel_file = pd.ExcelFile(input_file)
    
    finder = FreeDomainFinder()
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    
    total_found = 0
    total_missing = 0
    
    for sheet_name in excel_file.sheet_names:
        print(f"\n--- Traitement: {sheet_name} ---")
        df = pd.read_excel(input_file, sheet_name=sheet_name)
        
        # Identifie la colonne des noms d'entreprises
        company_col = None
        for col in df.columns:
            if 'account' in col.lower() or 'name' in col.lower():
                company_col = col
                break
        
        if not company_col:
            print(f"  ⚠️ Colonne entreprise non trouvée, feuille ignorée")
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            continue
        
        # Identifie ou crée la colonne domaine
        domain_col = None
        for col in ['Adresse générique du compte', 'Domain', 'Website', 'Site web']:
            if col in df.columns:
                domain_col = col
                break
        
        if not domain_col:
            domain_col = 'Domain'
            df[domain_col] = ''
        
        # Compte les domaines manquants
        missing_mask = df[domain_col].isna() | (df[domain_col] == '')
        missing_count = missing_mask.sum()
        
        print(f"  📊 {len(df)} lignes, {missing_count} domaines manquants")
        
        if missing_count == 0:
            print(f"  ✅ Aucun domaine manquant!")
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            continue
        
        # Traite seulement les entreprises sans domaine
        found_in_sheet = 0
        for idx in df[missing_mask].index:
            company_name = df.at[idx, company_col]
            
            # Ignore les lignes d'en-tête ou vides
            if pd.isna(company_name) or company_name in ['Active Customer', 'Étiquettes de lignes', 'Account Owner']:
                continue
            
            print(f"  🔍 {company_name}...")
            domain = finder.find_domain(company_name)
            
            if domain:
                df.at[idx, domain_col] = f"https://{domain}"
                found_in_sheet += 1
                total_found += 1
            
            total_missing += 1
            
            # Pause pour éviter le rate limiting
            time.sleep(2)
        
        print(f"  ✅ Trouvé: {found_in_sheet}/{missing_count}")
        
        # Sauvegarde la feuille
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    writer.close()
    
    print(f"\n\n🎉 Terminé!")
    print(f"📊 Résumé: {total_found}/{total_missing} domaines trouvés")
    print(f"💾 Fichier sauvegardé: {output_file}")

if __name__ == '__main__':
    input_file = '/Users/sylvainboue/Downloads/Sales - Territoires.xlsx'
    output_file = '/Users/sylvainboue/Downloads/Sales - Territoires - WITH DOMAINS.xlsx'
    
    process_excel_file(input_file, output_file)
