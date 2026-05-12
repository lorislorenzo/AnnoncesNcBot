import requests
import time
import json
import unicodedata
import re
import os
from dotenv import load_dotenv

#fonction qui vérifie les matchs
def annonce_match_keywords(titre, keywords):
    for mot in keywords:
        mot = normalize(mot)
        if re.search(rf"\b{re.escape(mot)}\b", titre):
            return True
    return False
#fonction pour gérer les accents
def normalize(text):
    text = text.lower()

    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
# url de l'api annonces.nc"
AlwaysAlertURL = "https://api.annonces.nc/posts?by_category=jeux-consoles-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1"
URL = [
    "https://api.annonces.nc/posts?sort=-created_at&per=30&by_site=annonces.nc&by_locality=nouvelle-caledonie",
    "https://api.annonces.nc/posts?by_category=tv-video-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    "https://api.annonces.nc/posts?by_category=informatique-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    "https://api.annonces.nc/posts?by_category=jeux-societe-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    "https://api.annonces.nc/posts?by_category=jouets-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    "https://api.annonces.nc/posts?by_category=livres-revues-bd-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    "https://api.annonces.nc/posts?by_category=collections-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    "https://api.annonces.nc/posts?by_category=divers-1&per=40&sort=-published_at&by_locality=nouvelle-caledonie&page=1",
    AlwaysAlertURL
]
# URL sur lequel je récupère l'intégralité des annonces

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
    # lance la requête pour récuper les annonces
    for url in URL :
        response = requests.get(url)
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
                if annonce_match_keywords(titre_annonce, KEYWORDS) or url == AlwaysAlertURL:
                    print(f"Nouveau match : {titre_annonce}")
                    # variable du message qui sera envoyé sur telegram
                    message = (
                    f"{titre_annonce}\n"
                    f"{price_annonce} XPF\n"
                    f'<a href="{annonce["link_url"]}">lien de l''annonce</a>'
                    )
                    # variable de mon url telegram + le message à envoyer
                    payload = {
                        "chat_id": CHAT_ID,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                    # envoie le message via le bot telegram
                    requests.post(url_telegram, data=payload)
                # si l'id n'est pas dans le json on le stock
                if id_annonce not in seen_ids:
                    new_ids.add(id_annonce)
                seen_ids.update(new_ids)
                # on ajoute les nouveaux id dans le json
            with open("seen.json", "w") as f:
                json.dump(list(seen_ids), f)
        # Attendre 5 minutes avant la prochaine requête
    time.sleep(300)  

# gérer les doublons