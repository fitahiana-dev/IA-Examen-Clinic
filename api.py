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