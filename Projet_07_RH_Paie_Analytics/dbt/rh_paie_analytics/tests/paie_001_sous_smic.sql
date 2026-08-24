{{ config(schema='anomalies_metier') }}

with paies_avec_smic as (
    select
        paies.matricule,
        paies.mois,
        paies.montant_total,
        smic.smic_horaire
    from {{ ref('stg_paies') }} as paies
    left join {{ ref('stg_smic_historique') }} as smic
        on date_trunc(paies.mois, month) = date_trunc(smic.mois, month)
)

select
    matricule,
    date_trunc(mois, month) as mois,
    'PAIE_001' as code_anomalie
from paies_avec_smic
where montant_total < (smic_horaire * 151.67 * 0.95)