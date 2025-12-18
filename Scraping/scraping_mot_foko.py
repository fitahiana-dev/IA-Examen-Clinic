import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import warnings
from urllib.parse import urljoin

# Désactiver les warnings SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)


class EthnicDictionaryScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Liste de toutes les ethnies
        self.ethnies = [
            'Bara', 'Betsileo', 'Betsimisaraka', 'Betsimisaraka Atsimo', 
            'Betsimisaraka Avaratra', 'Bezanozano', 'Mahafaly', 'Makoa',
            'Masikoro', 'Merina', 'Provincial', 'Saint-Marien', 'Sakalava',
            'Sakalava Atsimo', 'Sakalava Avaratra', 'Sakalava Nosy Be',
            'Sakalava-Mayotte', 'Sihanaka', 'Taifasy', 'Taimoro', 'Taisaka',
            'Tambahoaka', 'Tanala', 'Tandroy', 'Tankarana', 'Tanosy',
            'Tsimihety', 'Vakinankaratra', 'Vezo'
        ]
    
    def scrape_ethnic_words(self, ethnie):
        """Scrape les mots d'une ethnie spécifique en suivant tous les liens"""
        try:
            base_url = f"https://motmalgache.org/bins/ethnicLists?eth={ethnie}"
            print(f"  Scraping ethnie: {ethnie}...")
            
            response = self.session.get(base_url, timeout=15, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_words = []
            seen_words = set()
            word_links = []
            
            # 1. Extraire tous les liens de mots de la page principale
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Si c'est un lien vers une définition de mot
                if 'teny' in href or 'word' in href or len(text) > 0:
                    full_url = urljoin(base_url, href)
                    if text and text not in seen_words and text != '-':
                        seen_words.add(text)
                        all_words.append({
                            'mot': text,
                            'ethnie': ethnie,
                            'source': 'ethnic'
                        })
                        word_links.append(full_url)
            
            print(f"    → {len(all_words)} mots trouvés sur la page principale")
            print(f"    → Exploration des {len(word_links)} liens de mots...")
            
            # 2. Suivre chaque lien de mot pour extraire plus de vocabulaire
            for i, word_url in enumerate(word_links[:50], 1):  # Limite à 50 pour ne pas trop long
                if i % 10 == 0:
                    print(f"      ... progression: {i}/{min(50, len(word_links))}")
                
                try:
                    word_response = self.session.get(word_url, timeout=10, verify=False)
                    word_soup = BeautifulSoup(word_response.content, 'html.parser')
                    
                    # Extraire tous les mots de la page de définition
                    for row in word_soup.find_all('tr'):
                        for cell in row.find_all('td'):
                            text = cell.get_text().strip()
                            if text and len(text) > 0 and text not in seen_words and text != '-':
                                seen_words.add(text)
                                all_words.append({
                                    'mot': text,
                                    'ethnie': ethnie,
                                    'source': 'ethnic_deep'
                                })
                    
                    time.sleep(0.3)  # Petite pause entre chaque page
                    
                except Exception as e:
                    continue
            
            print(f"    ✓ Total: {len(all_words)} mots extraits (avec exploration)")
            return all_words
        
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
            return []
    
    def scrape_all_ethnies(self):
        """Scrape toutes les ethnies"""
        all_words = {}
        
        print("="*70)
        print("SCRAPING DES MOTS PAR ETHNIE MALGACHE")
        print("="*70)
        
        for i, ethnie in enumerate(self.ethnies, 1):
            print(f"\n[{i}/{len(self.ethnies)}] {ethnie}")
            words = self.scrape_ethnic_words(ethnie)
            
            if words:
                all_words[ethnie] = words
            
            time.sleep(0.5)  # Pause entre chaque ethnie
        
        return all_words
    
    def save_by_ethnie(self, all_words, output_dir='Dictionnaire/Ethnies'):
        """Sauvegarder un fichier par ethnie"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*70)
        print("SAUVEGARDE DES FICHIERS PAR ETHNIE")
        print("="*70)
        
        for ethnie, words in all_words.items():
            # Nettoyer le nom de fichier
            safe_name = ethnie.replace(' ', '_').replace('-', '_')
            filename = f"{output_dir}/{safe_name}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                for word in words:
                    f.write(word['mot'] + '\n')
            
            print(f"  ✓ {ethnie}: {len(words)} mots → {safe_name}.txt")
    
    def save_combined(self, all_words, output_dir='Dictionnaire'):
        """Sauvegarder un fichier combiné avec toutes les ethnies"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*70)
        print("SAUVEGARDE DU FICHIER COMBINÉ")
        print("="*70)
        
        # Format TXT (ethnie | mot)
        txt_file = f"{output_dir}/ethnies_combined.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            for ethnie, words in all_words.items():
                for word in words:
                    f.write(f"{ethnie} | {word['mot']}\n")
        print(f"  ✓ Fichier TXT: {txt_file} (format: ethnie | mot)")
        
        # Format JSON
        json_file = f"{output_dir}/ethnies_combined.json"
        json_data = {}
        for ethnie, words in all_words.items():
            json_data[ethnie] = [w['mot'] for w in words]
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Fichier JSON: {json_file}")
        
        # Format CSV (ethnie, mot)
        csv_file = f"{output_dir}/ethnies_combined.csv"
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Ethnie', 'Mot'])
            for ethnie, words in all_words.items():
                for word in words:
                    writer.writerow([ethnie, word['mot']])
        print(f"  ✓ Fichier CSV: {csv_file} (colonnes: Ethnie, Mot)")

    
    def show_statistics(self, all_words):
        """Afficher les statistiques"""
        print("\n" + "="*70)
        print("STATISTIQUES")
        print("="*70)
        
        total = 0
        sorted_ethnies = sorted(all_words.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"\n{'Ethnie':<30} {'Nombre de mots':>15}")
        print("-"*70)
        
        for ethnie, words in sorted_ethnies:
            count = len(words)
            total += count
            print(f"{ethnie:<30} {count:>15,}")
        
        print("-"*70)
        print(f"{'TOTAL':<30} {total:>15,}")
        
        # Mots uniques tous confondus
        all_unique_words = set()
        for words in all_words.values():
            for word in words:
                all_unique_words.add(word['mot'].lower())
        
        print(f"{'Mots uniques (total)':<30} {len(all_unique_words):>15,}")
        print("="*70)


def main():
    scraper = EthnicDictionaryScraper()
    
    # Scraper toutes les ethnies
    all_words = scraper.scrape_all_ethnies()
    
    if not all_words:
        print("\n❌ Aucun mot n'a été scraped.")
        return
    
    # Sauvegarder par ethnie (un fichier par ethnie)
    scraper.save_by_ethnie(all_words)
    
    # Sauvegarder le fichier combiné
    scraper.save_combined(all_words)
    
    # Afficher les statistiques
    scraper.show_statistics(all_words)
    
    print("\n" + "="*70)
    print("✅ SCRAPING TERMINÉ !")
    print("="*70)


if __name__ == "__main__":
    main()