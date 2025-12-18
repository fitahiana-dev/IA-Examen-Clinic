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

class MalagasyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_wikipedia_mg(self, url):
        """Scrape la page Wikipedia malgache"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            words = []
            # Chercher les mots dans le contenu principal
            content = soup.find('div', {'id': 'mw-content-text'})
            
            if content:
                # Extraire les liens (qui sont souvent des mots)
                for link in content.find_all('a'):
                    text = link.get_text().strip()
                    if text and len(text) > 2:  # Filtrer les mots trop courts
                        words.append({
                            'mot': text,
                            'url': urljoin(url, link.get('href', '')),
                            'source': 'wikipedia_mg'
                        })
                
                # Extraire aussi le texte des paragraphes
                for para in content.find_all('p'):
                    text = para.get_text().strip()
                    if text:
                        # Diviser en mots
                        mots_texte = text.split()
                        for mot in mots_texte:
                            mot_clean = mot.strip('.,;:!?()[]{}""\'')
                            if len(mot_clean) > 2:
                                words.append({
                                    'mot': mot_clean,
                                    'contexte': text[:100],
                                    'source': 'wikipedia_mg'
                                })
            
            return words
        
        except Exception as e:
            print(f"Erreur Wikipedia: {e}")
            return []
    
    def scrape_tenymalagasy(self, url):
        """Scrape le site tenymalagasy.org"""
        try:
            print("  Chargement de la page principale...")
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            words = []
            all_ranges = []
            seen_ranges = set()
            
            # Trouver tous les liens avec les plages (range parameter)
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'range=' in href and 'lang=mg' in href:
                    full_url = urljoin(url, href)
                    # Extraire juste le paramètre range pour éviter les doublons
                    range_param = href.split('range=')[1] if 'range=' in href else ''
                    if range_param and range_param not in seen_ranges:
                        seen_ranges.add(range_param)
                        all_ranges.append(full_url)
            
            print(f"  ✓ Trouvé {len(all_ranges)} plages de mots à scraper\n")
            
            # Scraper chaque plage
            for i, range_url in enumerate(all_ranges, 1):
                range_name = range_url.split('range=')[1] if 'range=' in range_url else 'unknown'
                print(f"  [{i}/{len(all_ranges)}] Plage: {range_name}")
                range_words = self.scrape_word_range(range_url)
                words.extend(range_words)
                time.sleep(0.5)  # Pause réduite à 0.5s
            
            return words
        
        except Exception as e:
            print(f"❌ Erreur Tenymalagasy: {e}")
            return []
    
    def scrape_word_range(self, url):
        """Scrape une plage spécifique de mots"""
        try:
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            words = []
            seen = set()  # Pour éviter les doublons dans la même page
            
            # Extraire tous les mots du tableau
            for row in soup.find_all('tr'):
                # Chercher dans toutes les cellules
                for cell in row.find_all('td'):
                    # Extraire le texte des liens
                    for link in cell.find_all('a'):
                        text = link.get_text().strip()
                        # Ne garder que les mots (pas les balises HTML vides)
                        if text and len(text) > 0 and text not in seen and text != '-':
                            seen.add(text)
                            words.append({
                                'mot': text,
                                'source': 'tenymalagasy'
                            })
            
            print(f"    → {len(words)} mots extraits")
            return words
        
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
            return []
    
    def scrape_word_list_from_letter(self, base_url, letter):
        """Scrape une liste de mots pour une lettre spécifique"""
        try:
            url = f"{base_url}/{letter}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            words = []
            # Adapter selon la structure HTML du site
            for item in soup.find_all(['li', 'div', 'span']):
                text = item.get_text().strip()
                if text and len(text) > 2:
                    words.append({
                        'mot': text,
                        'lettre': letter,
                        'source': 'letter_list'
                    })
            
            return words
        
        except Exception as e:
            print(f"Erreur lettre {letter}: {e}")
            return []
    
    def save_to_json(self, data, filename):
        """Sauvegarder en JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Sauvegardé dans {filename}")
    
    def save_to_csv(self, data, filename):
        """Sauvegarder en CSV"""
        if not data:
            print("Pas de données à sauvegarder")
            return
        
        keys = data[0].keys()
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"Sauvegardé dans {filename}")
    
    def save_to_txt(self, data, filename):
        """Sauvegarder dans un fichier texte (un mot par ligne)"""
        with open(filename, 'w', encoding='utf-8') as f:
            for word in data:
                f.write(word['mot'] + '\n')
        print(f"Sauvegardé {len(data)} mots dans {filename}")
    
    def remove_duplicates(self, words):
        """Enlever les doublons"""
        seen = set()
        unique = []
        for word in words:
            mot = word['mot'].lower()
            if mot not in seen:
                seen.add(mot)
                unique.append(word)
        return unique


def main():
    scraper = MalagasyScraper()
    
    # Créer le dossier Dictionnaire s'il n'existe pas
    os.makedirs('Dictionnaire', exist_ok=True)
    
    # URLs à scraper
    wikipedia_url = "https://mg.wikipedia.org/wiki/Wikipedia:Fandraisana"
    tenymalagasy_url = "https://motmalgache.org/bins/alphaLists"
    
    all_words = []
    
    # Scraper Wikipedia
    print("Scraping Wikipedia malgache...")
    wiki_words = scraper.scrape_wikipedia_mg(wikipedia_url)
    all_words.extend(wiki_words)
    print(f"Trouvé {len(wiki_words)} mots sur Wikipedia\n")
    time.sleep(1)  # Pause pour être poli avec le serveur
    
    # Scraper Tenymalagasy (toutes les plages)
    print("Scraping Motmalgache (toutes les plages)...")
    teny_words = scraper.scrape_tenymalagasy(tenymalagasy_url)
    all_words.extend(teny_words)
    print(f"\nTrouvé {len(teny_words)} mots sur Motmalgache")
    
    # Enlever les doublons
    all_words = scraper.remove_duplicates(all_words)
    print(f"\nTotal de mots uniques: {len(all_words)}")
    
    # Sauvegarder dans le dossier Dictionnaire
    scraper.save_to_txt(all_words, 'Dictionnaire/teny.txt')
    
    # Sauvegarder aussi en JSON et CSV pour référence
    scraper.save_to_json(all_words, 'Dictionnaire/mots_malgaches.json')
    scraper.save_to_csv(all_words, 'Dictionnaire/mots_malgaches.csv')
    
    # Afficher quelques exemples
    print("\nExemples de mots récupérés:")
    for word in all_words[:10]:
        print(f"- {word['mot']} (source: {word['source']})")


if __name__ == "__main__":
    main()