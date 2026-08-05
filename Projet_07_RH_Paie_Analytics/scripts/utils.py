import csv
import random
from datetime import date, timedelta
from faker import Faker
import requests
import pandas as pd


fake = Faker("fr_FR")
random.seed(42)  # reproductibilité

NB_SALARIES = 130
SEUIL_ANOMALIE_GENRE = 0.03      # 3% genre ≠ num sécu
SEUIL_ANOMALIE_DUPLICATA = 0.02  # 2% num sécu dupliqué
SEUIL_ANOMALIE_CSP = 0.04        # 4% erreur classification CSP

SERVICES = ["Production", "Commercial", "RH", "Finance", "IT", "Direction"]
CSP_VALIDES = ["Employé", "Agent de maîtrise", "Cadre"]

ORDRE_CSP = {"Employé": 0, "Agent de maîtrise": 1, "Cadre": 2}
SEUIL_MULTI_CONTRAT = 0.25          # 25% des salariés ont plusieurs contrats successifs
SEUIL_ANOMALIE_RETROGRADATION = 0.15  # 15% de ce sous-groupe subit une rétrogradation anormale

HEURES_MENSUELLES = 151.67
TAUX_COTISATION_PATRONALE = 0.42
TAUX_COTISATION_SALARIALE = 0.22
TAUX_AUGMENTATION_ANNUELLE = 1.015  # augmentation moyenne composée de 1,5%/an

SEUIL_ANOMALIE_DATES = 0.03          # 3% dates incohérentes (arrêt avant embauche, chevauchement)
SEUIL_ANOMALIE_MONTANT = 0.03        # 3% Base×Taux ≠ Montant
SEUIL_ANOMALIE_CONVERSION = 0.04     # 4% erreur conversion horaire→mensuel
SEUIL_ANOMALIE_SMIC = 0.02           # 2% salaire sous SMIC en vigueur

TYPES_EVENEMENT = ["Congé payé", "Arrêt maladie", "Congé maternité", "Congé paternité"]
POIDS_EVENEMENT = [0.6, 0.3, 0.06, 0.04]  # fréquence relative de chaque type

SMIC_PAR_DEFAUT = 11.88  # fallback si l'API est indisponible


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

        genre_reel_pour_secu = genre
        if random.random() < SEUIL_ANOMALIE_GENRE:
            genre_reel_pour_secu = "F" if genre == "H" else "H"

        numero_secu = generer_numero_secu(genre_reel_pour_secu, date_naissance)

        if numeros_utilises and random.random() < SEUIL_ANOMALIE_DUPLICATA:
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

        a_plusieurs_contrats = random.random() < SEUIL_MULTI_CONTRAT
        nb_contrats = random.randint(2, 3) if a_plusieurs_contrats else 1
        aura_retrogradation = a_plusieurs_contrats and random.random() < SEUIL_ANOMALIE_RETROGRADATION

        csp_courante = random.choices(CSP_VALIDES, weights=[0.5, 0.3, 0.2])[0]
        type_courant = "CDD" if a_plusieurs_contrats else random.choices(["CDD", "CDI"], weights=[0.2, 0.8])[0]
        date_debut_courante = date_embauche

        for n in range(nb_contrats):
            est_dernier = (n == nb_contrats - 1)

            if not est_dernier:
                duree_mois = random.randint(6, 18)
                date_fin_courante = date_debut_courante + timedelta(days=duree_mois * 30)
            else:
                date_fin_courante = None

            if n > 0:
                ordre_actuel = ORDRE_CSP[csp_courante]
                if aura_retrogradation and est_dernier and ordre_actuel > 0:
                    csp_courante = [c for c, o in ORDRE_CSP.items() if o == ordre_actuel - 1][0]
                elif random.random() < 0.5 and ordre_actuel < 2:
                    csp_courante = [c for c, o in ORDRE_CSP.items() if o == ordre_actuel + 1][0]

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


def recuperer_historique_smic_complet():
    """Un seul appel API pour récupérer tout l'historique SMIC (toutes dates de changement légal)."""
    try:
        url = "https://api.fr.openfisca.org/latest/parameter/marche_travail.salaire_minimum.smic.smic_b_horaire"
        reponse = requests.get(url, timeout=5)
        reponse.raise_for_status()
        return reponse.json().get("values", {})
    except Exception:
        return {}


def lire_csv(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generer_mois(date_debut, date_fin):
    mois_liste = []
    courant = date(date_debut.year, date_debut.month, 1)
    while courant <= date_fin:
        mois_liste.append(courant)
        if courant.month == 12:
            courant = date(courant.year + 1, 1, 1)
        else:
            courant = date(courant.year, courant.month + 1, 1)
    return mois_liste


def generer_table_smic(mois_liste):
    """Génère la table de référence SMIC : calendrier + jointure asof + fallback SMIC par défaut."""
    df_calendrier = pd.DataFrame({"mois": pd.to_datetime([m.isoformat() for m in mois_liste])})

    valeurs_api = recuperer_historique_smic_complet()
    df_smic = pd.DataFrame(
        [(pd.to_datetime(d), v) for d, v in valeurs_api.items()],
        columns=["mois", "smic_horaire"]
    ).sort_values("mois") if valeurs_api else pd.DataFrame(columns=["mois", "smic_horaire"])

    df_joint = pd.merge_asof(
        df_calendrier.sort_values("mois"), df_smic, on="mois", direction="backward"
    )
    df_joint["smic_horaire"] = df_joint["smic_horaire"].fillna(SMIC_PAR_DEFAUT)
    df_joint["mois"] = df_joint["mois"].dt.strftime("%Y-%m-%d")

    return df_joint.to_dict("records")


def generer_evenements(contrats):
    evenements = []
    evenement_id = 1

    for contrat in contrats:
        if random.random() > 0.4:
            continue

        date_debut_contrat = date.fromisoformat(contrat["date_debut"])
        date_fin_contrat = (
            date.fromisoformat(contrat["date_fin"]) if contrat["date_fin"] else date.today()
        )

        type_evenement = random.choices(TYPES_EVENEMENT, weights=POIDS_EVENEMENT)[0]

        if type_evenement == "Congé payé":
            duree = random.randint(5, 20)
        elif type_evenement == "Arrêt maladie":
            duree = random.randint(3, 45)
        elif type_evenement == "Congé maternité":
            duree = 16 * 7
        else:
            duree = 25

        ecart_max = max((date_fin_contrat - date_debut_contrat).days - duree, 1)
        date_debut_evt = date_debut_contrat + timedelta(days=random.randint(0, ecart_max))
        date_fin_evt = date_debut_evt + timedelta(days=duree)

        if random.random() < SEUIL_ANOMALIE_DATES:
            date_debut_evt = date_debut_contrat - timedelta(days=random.randint(5, 30))

        evenements.append({
            "id": evenement_id,
            "salarie_id": contrat["salarie_id"],
            "contrat_id": contrat["id"],
            "type_evenement": type_evenement,
            "date_debut": date_debut_evt.isoformat(),
            "date_fin": date_fin_evt.isoformat(),
        })
        evenement_id += 1

    return evenements


def calculer_montant(base, evenement_actif):
    """Applique les règles simplifiées selon le type d'événement en cours."""
    if evenement_actif is None:
        return base, "normal"

    type_evt = evenement_actif["type_evenement"]

    if type_evt == "Congé payé":
        return base, "normal"

    if type_evt == "Arrêt maladie":
        duree = (date.fromisoformat(evenement_actif["date_fin"]) -
                  date.fromisoformat(evenement_actif["date_debut"])).days
        taux = 0.90 if duree <= 30 else 0.6667
        return round(base * taux, 2), "arrêt maladie - à valider service paie"

    return round(base * 0.5, 2), "congé maternité/paternité - à traiter par le service paie"


def calculer_taux_horaire_reevalue(taux_horaire_initial, date_debut_contrat, mois, smic_par_mois):
    """Réévalue le taux horaire selon les années écoulées : augmentation moyenne 1.5%/an + alignement SMIC."""
    nb_annees = mois.year - date_debut_contrat.year
    taux_reevalue = taux_horaire_initial * (TAUX_AUGMENTATION_ANNUELLE ** nb_annees)

    smic_du_mois = smic_par_mois.get(mois.isoformat(), taux_horaire_initial)
    return round(max(taux_reevalue, smic_du_mois), 2)


def generer_paie(contrats, evenements, mois_liste, smic_par_mois):
    paies = []
    paie_id = 1

    evenements_par_salarie = {}
    for evt in evenements:
        evenements_par_salarie.setdefault(evt["salarie_id"], []).append(evt)

    for contrat in contrats:
        date_debut_contrat = date.fromisoformat(contrat["date_debut"])
        date_fin_contrat = (
            date.fromisoformat(contrat["date_fin"]) if contrat["date_fin"] else None
        )
        taux_horaire_initial = float(contrat["taux_horaire"])

        for mois in mois_liste:
            if mois < date_debut_contrat:
                continue
            if date_fin_contrat and mois > date_fin_contrat:
                continue

            taux_horaire = calculer_taux_horaire_reevalue(
                taux_horaire_initial, date_debut_contrat, mois, smic_par_mois
            )

            smic_du_mois = smic_par_mois[mois.isoformat()]

            base = round(taux_horaire * HEURES_MENSUELLES, 2)

            # Anomalie : salaire sous SMIC en vigueur
            if random.random() < SEUIL_ANOMALIE_SMIC:
                base = round(smic_du_mois * HEURES_MENSUELLES * 0.85, 2)

            evenement_actif = None
            for evt in evenements_par_salarie.get(contrat["salarie_id"], []):
                if evt["contrat_id"] != contrat["id"]:
                    continue
                d_debut = date.fromisoformat(evt["date_debut"])
                d_fin = date.fromisoformat(evt["date_fin"])
                if d_debut <= mois <= d_fin:
                    evenement_actif = evt
                    break

            montant, statut_paie = calculer_montant(base, evenement_actif)

            # Anomalie : conversion horaire → mensuel erronée (oubli du facteur 151,67h)
            if random.random() < SEUIL_ANOMALIE_CONVERSION:
                montant = round(taux_horaire, 2)

            taux_patronal = round(montant * TAUX_COTISATION_PATRONALE, 2)
            taux_salarial = round(montant * TAUX_COTISATION_SALARIALE, 2)

            # Anomalie : Base × Taux ≠ Montant
            if random.random() < SEUIL_ANOMALIE_MONTANT:
                montant = round(montant * random.uniform(1.1, 1.3), 2)

            paies.append({
                "id": paie_id,
                "salarie_id": contrat["salarie_id"],
                "contrat_id": contrat["id"],
                "mois": mois.isoformat(),
                "base": base,
                "taux_horaire": taux_horaire,
                "taux_patronal": taux_patronal,
                "taux_salarial": taux_salarial,
                "montant_total": montant,
                "statut_paie": statut_paie,
            })
            paie_id += 1

    return paies


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