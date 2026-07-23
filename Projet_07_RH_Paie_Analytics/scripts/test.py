import requests, time

start = time.time()
url = "https://api.fr.openfisca.org/latest/parameter/marche_travail.salaire_minimum.smic.smic_b_horaire"

try:
    reponse = requests.get(url, timeout=5)
    print(f"Temps de réponse : {time.time() - start:.2f}s")
    print(f"Code statut : {reponse.status_code}")
    if reponse.status_code == 200:
        print(reponse.json())
    else:
        print("Erreur : réponse non 200")
except Exception as e:
    print(f"Exception levée : {e}")