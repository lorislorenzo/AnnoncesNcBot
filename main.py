import requests
import time
import json
import unicodedata
import re
import os
from dotenv import load_dotenv

#fonction pour gérer les accents
def normalize(text):
    text = text.lower()

    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
# url de l'api annonces.nc"
URL = "https://api.annonces.nc/posts?sort=-created_at&per=30&by_site=annonces.nc&by_locality=nouvelle-caledonie" 
# id de mon token telegram
load_dotenv()
TOKEN = os.getenv("TOKEN")
# mon id telegram
CHAT_ID = os.getenv("CHAT_ID")
# variable de l'url telegram pour envoyer les messages via le bot (token)
url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
# charge le json avec les mots recherchés
with open("keywords.json", "r") as f: 
    data_keywords = json.load(f)   
KEYWORDS = data_keywords["keywords"]

# on vérifie si on a déjà vu les annonces grâce à l'id
try:
    with open("seen.json", "r") as f:
        seen_ids = set(json.load(f))
except:  # noqa: E722
    seen_ids = set()

while True:
    new_ids = set()
    # ance la requête pour récuper les annonces
    response = requests.get(URL)
    # on stock les données dans une variable
    data = response.json()
    # parcourir les annonces et stock les id et les titres
    for annonce in data:
        id_annonce = annonce["id"]
        titre_annonce = normalize(annonce["title"])
        price_annonce = annonce["price"]
        # on vérifie si l'id n'est pas dans le json des id
        if id_annonce not in seen_ids:
        # boucle pour vérifier si un mot clé est dans le titre de l'annonce
            for mot in KEYWORDS:
                mot = normalize(mot)
                if re.search(rf"\b{re.escape(mot)}\b", titre_annonce):
                    print(f"Nouveau match : {titre_annonce}")
                # variable du message qui sera envoyé sur telegram
                    message = f"""
                    🔥 Nouveau match !
                    Titre : {titre_annonce}
                    Prix : {price_annonce} XPF
                    <a href="{annonce['link_url']}">Voir l'annonce</a>
                    """
                    # variable de mon url telegram + le message à envoyer
                    payload = {
                        "chat_id": CHAT_ID,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                    # envoie le message via le bot telegram
                    response_telegram = requests.post(url_telegram, data=payload)
                    print(response_telegram.status_code)
                    print(response_telegram.text)
                    # break pour éviter d'envoyer plusieurs messages pour la même annonce si elle contient plusieurs mots clés
                    break
            # si l'id n'est pas dans le json on le stock
            
            if id_annonce not in seen_ids:
                new_ids.add(id_annonce)
        seen_ids.update(new_ids)
            # on ajoute les nouveaux id dans le json
    with open("seen.json", "w") as f:
        json.dump(list(seen_ids), f)
    # Attendre 1 minute avant la prochaine requête
    time.sleep(60)  

# gérer les doublons