from typing import Union
from fastapi import FastAPI

#Importer les Modules IA
from module_IA import levenshtein

app = FastAPI()


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
    return {"closed_word":"exemple"}