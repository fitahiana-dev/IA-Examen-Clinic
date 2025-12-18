from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#Importer les Modules IA
from module_IA import levenshtein

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3000"],  # ou "*" pour test
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

#Endpoint pour Obtenir mot proche
@app.get("/getClosedWord/{word}")
def closed_word(word:str):
    a_comparator=levenshtein.Levenshtein("Dictionnaire/teny_clean.txt")
    mot_proche,dist=a_comparator.mot_proche(word)
    return {"closed_word":mot_proche,"distance":dist}

#Endpoint pour detecter si un mot appartient au dictionnaire Malagasy
@app.get("/verifyWord/{word}")
def verify_word(word:str):
    pass

#######################################################################
#######################################################################
from pydantic import BaseModel
import re
import os

DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), "Dictionnaire/teny_clean.txt")
VALID_WORDS = set()

try:
    with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
        # On suppose un mot par ligne dans teny_clean.txt
        content = f.read().splitlines()
        VALID_WORDS = set(word.strip().lower() for word in content if word.strip())
    print(f"✅ Dictionnaire chargé : {len(VALID_WORDS)} mots.")
except FileNotFoundError:
    print(f"❌ ERREUR : Impossible de trouver le fichier {DICTIONARY_PATH}")


# Modèle de données reçu depuis React
class TextPayload(BaseModel):
    text: str

#Endpoint Verification le mot Fait partie du Dictionnaire
@app.post("/check_spelling")
def check_spelling(payload: TextPayload):
    """
    Reçoit un texte, découpe les mots, et renvoie ceux qui ne sont pas dans le dictionnaire.
    """
    text = payload.text
    # Regex pour isoler les mots (enlève ponctuation, chiffres)
    words = re.findall(r"\b[a-zA-Zà-ÿÀ-Ÿ-]+\b", text)
    
    unknown_words = []
    
    for word in words:
        clean_word = word.lower()
        # Ignorer les mots très courts (1 lettre) ou s'ils sont dans le dico
        if len(clean_word) > 1 and clean_word not in VALID_WORDS:
            unknown_words.append(word)
            
    # On renvoie la liste unique pour éviter les doublons
    return {"unknown": list(set(unknown_words))}