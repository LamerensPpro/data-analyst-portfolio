from datetime import date
""""
from utils import (
    generer_salaries, generer_contrats, generer_mois,
    generer_table_smic, generer_evenements, generer_paie,
    sauvegarder_csv, NB_SALARIES
)
"""
import utils

if __name__ == "__main__":
    salaries = utils.generer_salaries(utils.NB_SALARIES)
    contrats = utils.generer_contrats(salaries)

    utils.sauvegarder_csv(
        salaries, "data/raw/salaries.csv",
        ["id", "nom", "prenom", "genre", "date_naissance", "numero_secu", "date_embauche"]
    )
    utils.sauvegarder_csv(
        contrats, "data/raw/contrats.csv",
        ["id", "salarie_id", "date_debut", "date_fin", "csp", "service", "type_contrat", "temps_travail", "taux_horaire"]
    )

    print(f"{len(salaries)} salariés générés → data/raw/salaries.csv")
    print(f"{len(contrats)} contrats générés → data/raw/contrats.csv")

    dates_debut = [date.fromisoformat(c["date_debut"]) for c in contrats]
    mois_liste = utils.generer_mois(min(dates_debut), date.today())

    smic_historique = utils.generer_table_smic(mois_liste)
    smic_par_mois = {ligne["mois"]: ligne["smic_horaire"] for ligne in smic_historique}

    evenements = utils.generer_evenements(contrats)
    paies = utils.generer_paie(contrats, evenements, mois_liste, smic_par_mois)

    utils.sauvegarder_csv(
        evenements, "data/raw/evenements.csv",
        ["id", "salarie_id", "contrat_id", "type_evenement", "date_debut", "date_fin"]
    )
    utils.sauvegarder_csv(
        paies, "data/raw/paies.csv",
        ["id", "salarie_id", "contrat_id", "mois", "base", "taux_horaire",
         "taux_patronal", "taux_salarial", "montant_total", "statut_paie"]
    )
    utils.sauvegarder_csv(smic_historique, "data/raw/smic_historique.csv", ["mois", "smic_horaire"])

    print(f"{len(evenements)} événements générés → data/raw/evenements.csv")
    print(f"{len(paies)} bulletins de paie générés → data/raw/paies.csv")
    print(f"{len(smic_historique)} mois SMIC générés → data/raw/smic_historique.csv")