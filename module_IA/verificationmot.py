import re
import sys
import argparse
from typing import List, Set

class MalagasySpellChecker:
    """
    Correcteur orthographique professionnel pour le malgache.
    - Alphabet strict : 21 lettres (pas de c, q, u, w, x)
    - Détection renforcée des lettres interdites mot par mot
    - 'y' seulement en fin de mot
    - Pas de mot finissant par 'i' (doit être 'y')
    - Clusters limités (mp, mb, nt, nd, nk, ng, tr, dr, ts, dz, ty, dy...)
    - Pas de géminées (kk, pp, tt)
    - Pas de 3 consonnes consécutives
    """

    # Lettres autorisées (21 lettres)
    ALLOWED_LETTERS = set('abdefghijklmnorstvyzABDEFGHIJKLMNORSTVYZ')

    # Lettres strictement interdites (c, q, u, w, x)
    FORBIDDEN_LETTERS = set('cquwxCQUWX')

    # Voyelles
    VOWELS = set('aeiouAEIOU')

    # Clusters autorisés (internes + terminaisons avec y)
    ALLOWED_CLUSTERS = {
        'mp', 'mb', 'nt', 'nd', 'nk', 'ng', 'ns', 'nts', 'ndz', 'ntr', 'ndr',
        'tr', 'dr', 'ts', 'dz',
        'ty', 'dy', 'fy', 'my', 'ky', 'gy', 'py', 'by', 'ny', 'ry', 'sy', 'hy', 'ly', 'vy', 'jy'
    }

    # Regex pour géminées
    RE_GEMINATED = re.compile(r'([bcdfghjklmnpqrstvwxyz])\1', re.IGNORECASE)

    # Regex pour 'y' au milieu d'un mot
    RE_Y_MIDDLE = re.compile(r'\w*y\w', re.IGNORECASE)

    # Regex pour 3 consonnes consécutives
    RE_THREE_CONSONANTS = re.compile(r'[^aeiouAEIOU]{3}', re.IGNORECASE)

    def __init__(self):
        self.allowed_pattern = r'(?:' + '|'.join(re.escape(c) for c in self.ALLOWED_CLUSTERS) + r')'
        self.re_allowed = re.compile(self.allowed_pattern, re.IGNORECASE)

    def check_text(self, text: str) -> List[str]:
        errors = []

        # 1. Lettres interdites (renforcé : mot par mot)
        words = re.findall(r'\b\w+\b', text)
        forbidden_words = []
        for word in words:
            if any(letter in self.FORBIDDEN_LETTERS for letter in word):
                forbidden_words.append(word)
        if forbidden_words:
            errors.append(f"Mots contenant lettres interdites (c, q, u, w, x) : {', '.join(set(forbidden_words))} "
                          f"(remplacez : ex. 'computer' → 'kômpiotera', 'quick' → 'kika').")

        # 2. Géminées (kk, pp, tt...)
        if self.RE_GEMINATED.search(text):
            errors.append("Géminées détectées (ex. kk, pp, tt) : rares en malgache.")

        # 3. 3 consonnes consécutives
        if self.RE_THREE_CONSONANTS.search(text):
            errors.append("Trois consonnes consécutives : interdit en malgache.")

        # 4. 'y' au milieu d'un mot
        if self.RE_Y_MIDDLE.search(text):
            errors.append("Le 'y' ne doit apparaître qu'en fin de mot (ex. fady, maty, teny).")

        # 5. Mots finissant par 'i' (interdit : doit être 'y')
        forbidden_end_i = [word for word in words if word.lower().endswith('i')]
        if forbidden_end_i:
            errors.append(f"Mots finissant par 'i' (interdit) : {', '.join(set(forbidden_end_i))} "
                          f"(utilisez 'y' : ex. maty au lieu de mati).")

        # 6. Clusters interdits (paires de consonnes internes)
        cleaned = re.sub(r'\s+', '', text.lower())
        consonant_pairs = re.findall(r'([bcdfghjklmnpqrstvwxyz][bcdfghjklmnpqrstvwxyz])', cleaned)

        forbidden_pairs = []
        for pair in consonant_pairs:
            if pair.lower() in self.ALLOWED_CLUSTERS:
                continue
            if re.search(rf'{pair}y$', cleaned):
                continue
            forbidden_pairs.append(pair)

        if forbidden_pairs:
            unique = set(forbidden_pairs)
            errors.append(f"Combinaisons interdites internes : {', '.join(unique)} "
                          f"(autorisé : mp, mb, nt, nd, nk, ng, tr, dr, ts, dz, ty, dy, etc.).")

        return errors

    def validate(self, text: str) -> str:
        errors = self.check_text(text)
        if errors:
            return "Erreurs détectées :\n" + "\n".join(f"- {err}" for err in errors)
        return "Texte correct selon les règles orthographiques du malgache !"

def main():
    parser = argparse.ArgumentParser(description="Vérificateur orthographique malgache (règles complètes).")
    parser.add_argument("text", nargs="*", help="Texte à vérifier")
    parser.add_argument("-f", "--file", help="Fichier texte à vérifier")
    args = parser.parse_args()

    checker = MalagasySpellChecker()

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Vérification du fichier : {args.file}")
            print(checker.validate(text))
        except Exception as e:
            print(f"Erreur de lecture : {e}")
    elif args.text:
        text = ' '.join(args.text)
        print(checker.validate(text))
    else:
        print("Vérificateur orthographique malgache (tape 'quit' pour quitter)")
        print("Exemples : faty (OK), computer (erreur), mati (erreur i), manonboka (erreur nb)")
        while True:
            text = input("\nTexte à vérifier : ").strip()
            if text.lower() == 'quit':
                print("Au revoir !")
                break
            if text:
                print(checker.validate(text))
            else:
                print("Entrez un texte valide.")

if __name__ == "__main__":
    main()