import re
import os

class TextCleaner:
    def __init__(self, input_file, output_file=None):
        self.input_file = input_file
        self.output_file = output_file or input_file.replace('.txt', '_clean.txt')
    
    def remove_parentheses_content(self, text):
        """Enlever tout ce qui est entre parenthèses, y compris les parenthèses"""
        # Enlever le contenu entre parenthèses (incluant les parenthèses)
        text = re.sub(r'\([^)]*\)', '', text)
        return text
    
    def clean_line(self, line):
        """Nettoyer une ligne complètement"""
        # Enlever les parenthèses et leur contenu
        line = self.remove_parentheses_content(line)
        
        # Enlever tout ce qui est après "/" (pour enlever les traductions arabes, etc.)
        line = re.sub(r'/.*', '', line)
        
        # Enlever les crochets et leur contenu [...]
        line = re.sub(r'\[.*?\]', '', line)
        
        # Enlever les chiffres isolés ou en groupe
        line = re.sub(r'\d+', '', line)
        
        # Enlever les caractères spéciaux mais garder les lettres accentuées
        # Garde : lettres, espaces, traits d'union, apostrophes
        line = re.sub(r'[^\w\s\-\'ÃÂÁÀÄÅÆÇÉÈÊËÍÌÎÏÑÓÒÔÖØÚÙÛÜÝãâáàäåæçéèêëíìîïñóòôöøúùûüýÿ]', '', line)
        
        # Enlever les espaces multiples
        line = re.sub(r'\s+', ' ', line)
        
        # Enlever les espaces au début et à la fin
        line = line.strip()
        
        return line
    
    def clean_file(self, keep_empty_lines=False):
        """Nettoyer tout le fichier"""
        try:
            # Lire le fichier original
            with open(self.input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Lecture de {len(lines)} lignes...")
            
            # Nettoyer chaque ligne
            cleaned_lines = []
            for line in lines:
                cleaned = self.clean_line(line)
                
                # Garder la ligne si elle n'est pas vide ou si on garde les lignes vides
                if cleaned or keep_empty_lines:
                    cleaned_lines.append(cleaned)
            
            # Sauvegarder le fichier nettoyé
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for line in cleaned_lines:
                    f.write(line + '\n')
            
            print(f"✓ Fichier nettoyé sauvegardé : {self.output_file}")
            print(f"  - Lignes originales : {len(lines)}")
            print(f"  - Lignes nettoyées : {len(cleaned_lines)}")
            print(f"  - Lignes supprimées : {len(lines) - len(cleaned_lines)}")
            
            return cleaned_lines
        
        except FileNotFoundError:
            print(f"❌ Erreur : Le fichier '{self.input_file}' n'existe pas")
            return []
        except Exception as e:
            print(f"❌ Erreur : {e}")
            return []
    
    def remove_duplicates(self):
        """Enlever les doublons du fichier nettoyé"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Enlever les doublons en gardant l'ordre
            seen = set()
            unique_lines = []
            for line in lines:
                line_lower = line.strip().lower()
                if line_lower and line_lower not in seen:
                    seen.add(line_lower)
                    unique_lines.append(line.strip())
            
            # Sauvegarder
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for line in unique_lines:
                    f.write(line + '\n')
            
            print(f"✓ Doublons supprimés : {len(lines) - len(unique_lines)}")
            print(f"  - Mots uniques : {len(unique_lines)}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la suppression des doublons : {e}")
    
    def show_preview(self, num_lines=10):
        """Afficher un aperçu du fichier nettoyé"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"\n📋 Aperçu des {min(num_lines, len(lines))} premières lignes :")
            print("-" * 50)
            for i, line in enumerate(lines[:num_lines], 1):
                print(f"{i:3d}. {line.strip()}")
            print("-" * 50)
        
        except Exception as e:
            print(f"❌ Erreur : {e}")


def main():
    # Chemin vers le fichier
    input_file = 'Dictionnaire/teny.txt'
    output_file = 'Dictionnaire/teny_clean.txt'
    
    print("🧹 Nettoyage du fichier teny.txt...")
    print("=" * 60)
    
    # Créer le nettoyeur
    cleaner = TextCleaner(input_file, output_file)
    
    # Nettoyer le fichier (ne garde pas les lignes vides)
    cleaner.clean_file(keep_empty_lines=False)
    
    # Enlever les doublons
    print("\n🔍 Suppression des doublons...")
    cleaner.remove_duplicates()
    
    # Afficher un aperçu
    cleaner.show_preview(20)
    
    print(f"\n✅ Terminé ! Fichier nettoyé : {output_file}")


if __name__ == "__main__":
    main()