"""
Génération des données Paie + Événement + SMIC historique (Projet 7 - RH/Paie Analytics)
Anomalies injectées : dates incohérentes, Base×Taux≠Montant,
conversion horaire→mensuel erronée, salaire sous SMIC
"""

import csv
import random
import requests
from datetime import date, timedelta

random.seed(42)  # reproductibilité

HEURES_MENSUELLES = 151.67
TAUX_COTISATION_PATRONALE = 0.42
TAUX_COTISATION_SALARIALE = 0.22

TAUX_ANOMALIE_DATES = 0.03          # 3% dates incohérentes (arrêt avant embauche, chevauchement)
TAUX_ANOMALIE_MONTANT = 0.03        # 3% Base×Taux ≠ Montant
TAUX_ANOMALIE_CONVERSION = 0.04     # 4% erreur conversion horaire→mensuel
TAUX_ANOMALIE_SMIC = 0.02           # 2% salaire sous SMIC en vigueur

TYPES_EVENEMENT = ["Congé payé", "Arrêt maladie", "Congé maternité", "Congé paternité"]
POIDS_EVENEMENT = [0.6, 0.3, 0.06, 0.04]  # fréquence relative de chaque type

SMIC_PAR_DEFAUT = 11.88  # fallback si l'API est indisponible


def recuperer_smic(annee_mois):
    """Récupère le SMIC horaire en vigueur via l'API OpenFisca. Fallback si erreur réseau."""
    try:
        url = "https://api.fr.openfisca.org/latest/parameter/marche_travail.salaire_minimum.smic.smic_h_b"
        reponse = requests.get(url, timeout=5)
        reponse.raise_for_status()
        valeurs = reponse.json().get("values", {})
        dates_valides = [d for d in valeurs if d <= annee_mois]
        if dates_valides:
            date_retenue = max(dates_valides)
            return valeurs[date_retenue]
    except Exception:
        pass
    return SMIC_PAR_DEFAUT


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
    """Génère la table de référence SMIC : un seul appel API par mois distinct."""
    smic_historique = []
    for mois in mois_liste:
        smic_horaire = recuperer_smic(mois.isoformat())
        smic_historique.append({
            "mois": mois.isoformat(),
            "smic_horaire": smic_horaire,
        })
    return smic_historique


def generer_evenements(contrats):
    evenements = []
    evenement_id = 1

    for contrat in contrats:
        if random.random() > 0.4:  # ~40% des contrats ont un événement
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

        # Anomalie : dates incohérentes (arrêt commençant avant l'embauche)
        if random.random() < TAUX_ANOMALIE_DATES:
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
        taux_horaire = float(contrat["taux_horaire"])

        for mois in mois_liste:
            if mois < date_debut_contrat:
                continue
            if date_fin_contrat and mois > date_fin_contrat:
                continue

            smic_du_mois = smic_par_mois[mois.isoformat()]

            base = round(taux_horaire * HEURES_MENSUELLES, 2)

            # Anomalie : salaire sous SMIC en vigueur
            if random.random() < TAUX_ANOMALIE_SMIC:
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
            if random.random() < TAUX_ANOMALIE_CONVERSION:
                montant = round(taux_horaire, 2)

            taux_patronal = round(montant * TAUX_COTISATION_PATRONALE, 2)
            taux_salarial = round(montant * TAUX_COTISATION_SALARIALE, 2)

            # Anomalie : Base × Taux ≠ Montant
            if random.random() < TAUX_ANOMALIE_MONTANT:
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
    contrats = lire_csv("data/raw/contrats.csv")

    dates_debut = [date.fromisoformat(c["date_debut"]) for c in contrats]
    mois_liste = generer_mois(min(dates_debut), date.today())

    smic_historique = generer_table_smic(mois_liste)
    smic_par_mois = {ligne["mois"]: ligne["smic_horaire"] for ligne in smic_historique}

    evenements = generer_evenements(contrats)
    paies = generer_paie(contrats, evenements, mois_liste, smic_par_mois)

    sauvegarder_csv(
        evenements, "data/raw/evenements.csv",
        ["id", "salarie_id", "contrat_id", "type_evenement", "date_debut", "date_fin"]
    )
    sauvegarder_csv(
        paies, "data/raw/paies.csv",
        ["id", "salarie_id", "contrat_id", "mois", "base", "taux_horaire",
         "taux_patronal", "taux_salarial", "montant_total", "statut_paie"]
    )
    sauvegarder_csv(smic_historique, "data/raw/smic_historique.csv", ["mois", "smic_horaire"])

    print(f"{len(evenements)} événements générés → data/raw/evenements.csv")
    print(f"{len(paies)} bulletins de paie générés → data/raw/paies.csv")
    print(f"{len(smic_historique)} mois SMIC générés → data/raw/smic_historique.csv")