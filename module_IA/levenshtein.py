class Levenshtein:
    def __init__(self,lienDico):
        self.charger_dico(lienDico)

    # Alogirthme De Levenshtein
    def levenshtein(self,a: str, b: str) -> int:
        n, m = len(a), len(b)

        # Création de la matrice (n+1) x (m+1)
        dp = [[0] * (m + 1) for _ in range(n + 1)]

        # Initialisation
        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        # Remplissage
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,        # suppression
                    dp[i][j - 1] + 1,        # insertion
                    dp[i - 1][j - 1] + cost  # substitution
                )

        return dp[n][m]


    #Chargement des mots dans le Dictionnaire
    def charger_dico(self,path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    
    def mot_proche(self,word,dico):
        best_word = None
        best_dist = float("inf")

        for w in dico:
            d = self.levenshtein(word, w)
            if d < best_dist:
                best_dist = d
                best_word = w

        return best_word, best_dist


if __name__=="__main__":
    a="Mère"
    b="Mare"