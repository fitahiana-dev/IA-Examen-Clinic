import requests
from bs4 import BeautifulSoup
import json
import urllib3
import string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scrape_root_lists_first_td(url):
    """
    Scrape le texte des liens <a href> qui commencent par /bins/teny2/
    dans le premier <td> de chaque ligne <tr> de la page rootLists.
    
    Returns:
        liste de mots récupérés
    """
    try:
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        words = []
        for row in soup.find_all('tr'):
            first_td = row.find('td')
            if first_td:
                link = first_td.find('a', href=lambda x: x and x.startswith('/bins/teny2/'))
                if link:
                    word = link.get_text(strip=True)
                    if word:
                        words.append(word)
        print(f"{len(words)} mots trouvés sur {url}")
        return words

    except Exception as e:
        print(f"Erreur lors du scraping de {url}: {e}")
        return []


def save_words_to_json(words, filename='fototeny.json'):
    """Sauvegarde les mots dans un fichier JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"{len(words)} mots sauvegardés dans {filename}")


def save_words_to_txt(words, filename='fototeny.txt'):
    """Sauvegarde tous les mots dans un fichier texte (liste simple)."""
    with open(filename, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(word + '\n')
    print(f"{len(words)} mots sauvegardés dans {filename}")


if __name__ == "__main__":
    all_words = []

    # Alphabet malgache (ici a-z, adapte si nécessaire)
    letters = string.ascii_lowercase

    for letter in letters:
        url = f"https://tenymalagasy.org/bins/rootLists?o=let{letter}"
        words = scrape_root_lists_first_td(url)
        all_words.extend(words)

    # Supprimer les doublons
    all_words = sorted(list(set(all_words)))

    # Sauvegarder les résultats
    save_words_to_txt(all_words)
