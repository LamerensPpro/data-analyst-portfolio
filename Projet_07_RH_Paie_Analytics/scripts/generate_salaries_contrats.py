"""
Génération des données Salarié + Contrat (Projet 7 - RH/Paie Analytics)
Anomalies injectées : genre ≠ numéro sécu, numéro sécu dupliqué, erreur CSP
"""

import csv
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker("fr_FR")
random.seed(42)  # reproductibilité

NB_SALARIES = 130
TAUX_ANOMALIE_GENRE = 0.03      # 3% genre ≠ num sécu
TAUX_ANOMALIE_DUPLICATA = 0.02  # 2% num sécu dupliqué
TAUX_ANOMALIE_CSP = 0.04        # 4% erreur classification CSP

SERVICES = ["Production", "Commercial", "RH", "Finance", "IT", "Direction"]
CSP_VALIDES = ["Employé", "Agent de maîtrise", "Cadre"]

ORDRE_CSP = {"Employé": 0, "Agent de maîtrise": 1, "Cadre": 2}
TAUX_MULTI_CONTRAT = 0.25          # 25% des salariés ont plusieurs contrats successifs
TAUX_ANOMALIE_RETROGRADATION = 0.15  # 15% de ce sous-groupe subit une rétrogradation anormale



def generer_numero_secu(genre, date_naissance):
    """Génère un NIR simplifié cohérent (sexe, année, mois)."""
    sexe = "1" if genre == "H" else "2"
    annee = str(date_naissance.year)[2:]
    mois = f"{date_naissance.month:02d}"
    reste = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{sexe}{annee}{mois}{reste}"


def generer_salaries(nb):
    salaries = []
    numeros_utilises = []

    for i in range(1, nb + 1):
        genre = random.choice(["H", "F"])
        prenom = fake.first_name_male() if genre == "H" else fake.first_name_female()
        nom = fake.last_name()
        date_naissance = fake.date_of_birth(minimum_age=20, maximum_age=62)
        date_embauche = fake.date_between(start_date="-10y", end_date="-1M")

        # Anomalie : genre déclaré ≠ genre encodé dans le numéro de sécu
        genre_reel_pour_secu = genre
        if random.random() < TAUX_ANOMALIE_GENRE:
            genre_reel_pour_secu = "F" if genre == "H" else "H"

        numero_secu = generer_numero_secu(genre_reel_pour_secu, date_naissance)

        # Anomalie : numéro de sécu dupliqué (réutilise un numéro déjà généré)
        if numeros_utilises and random.random() < TAUX_ANOMALIE_DUPLICATA:
            numero_secu = random.choice(numeros_utilises)
        else:
            numeros_utilises.append(numero_secu)

        salaries.append({
            "id": i,
            "nom": nom,
            "prenom": prenom,
            "genre": genre,
            "date_naissance": date_naissance.isoformat(),
            "numero_secu": numero_secu,
            "date_embauche": date_embauche.isoformat(),
        })

    return salaries



def generer_contrats(salaries):
    contrats = []
    contrat_id = 1

    for salarie in salaries:
        date_embauche = date.fromisoformat(salarie["date_embauche"])

        a_plusieurs_contrats = random.random() < TAUX_MULTI_CONTRAT
        nb_contrats = random.randint(2, 3) if a_plusieurs_contrats else 1
        aura_retrogradation = a_plusieurs_contrats and random.random() < TAUX_ANOMALIE_RETROGRADATION

        csp_courante = random.choices(CSP_VALIDES, weights=[0.5, 0.3, 0.2])[0]
        type_courant = "CDD" if a_plusieurs_contrats else random.choices(["CDD", "CDI"], weights=[0.2, 0.8])[0]
        date_debut_courante = date_embauche

        for n in range(nb_contrats):
            est_dernier = (n == nb_contrats - 1)

            # Durée du contrat (sauf le dernier, toujours en cours)
            if not est_dernier:
                duree_mois = random.randint(6, 18)
                date_fin_courante = date_debut_courante + timedelta(days=duree_mois * 30)
            else:
                date_fin_courante = None

            # Évolution CSP à partir du 2e contrat
            if n > 0:
                ordre_actuel = ORDRE_CSP[csp_courante]
                if aura_retrogradation and est_dernier and ordre_actuel > 0:
                    # Anomalie : rétrogradation sur le dernier contrat
                    csp_courante = [c for c, o in ORDRE_CSP.items() if o == ordre_actuel - 1][0]
                elif random.random() < 0.5 and ordre_actuel < 2:
                    # Évolution normale : promotion
                    csp_courante = [c for c, o in ORDRE_CSP.items() if o == ordre_actuel + 1][0]

            # Évolution type de contrat : CDD -> CDI classique
            if n > 0 and type_courant == "CDD" and random.random() < 0.7:
                type_courant = "CDI"

            temps_travail = random.choices(["Temps plein", "Temps partiel"], weights=[0.85, 0.15])[0]
            taux_horaire = round(random.uniform(11.88, 35.0), 2)

            contrats.append({
                "id": contrat_id,
                "salarie_id": salarie["id"],
                "date_debut": date_debut_courante.isoformat(),
                "date_fin": date_fin_courante.isoformat() if date_fin_courante else "",
                "csp": csp_courante,
                "service": random.choice(SERVICES),
                "temps_travail": temps_travail,
                "type_contrat": type_courant,
                "taux_horaire": taux_horaire,
            })
            contrat_id += 1

            if date_fin_courante:
                date_debut_courante = date_fin_courante + timedelta(days=1)

    return contrats

def sauvegarder_csv(donnees, chemin, colonnes):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(donnees)


if __name__ == "__main__":
    salaries = generer_salaries(NB_SALARIES)
    contrats = generer_contrats(salaries)

    sauvegarder_csv(
        salaries, "data/raw/salaries.csv",
        ["id", "nom", "prenom", "genre", "date_naissance", "numero_secu", "date_embauche"]
    )
    sauvegarder_csv(
        contrats, "data/raw/contrats.csv",
        ["id", "salarie_id", "date_debut", "date_fin", "csp", "service","type_contrat", "temps_travail", "taux_horaire"]
    )

    print(f"{len(salaries)} salariés générés → data/raw/salaries.csv")
    print(f"{len(contrats)} contrats générés → data/raw/contrats.csv")