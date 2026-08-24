with source as (
    select * from {{ source('raw', 'raw_paies') }}
)

select
    cast(id as int64) as paie_id,
    cast(salarie_id as int64) as matricule,
    cast(contrat_id as int64) as contrat_id,
    cast(mois as date) as mois,
    safe_cast(evenement_id as int64) as evenement_id,
    cast(base as float64) as base,
    cast(taux_horaire as float64) as taux_horaire,
    cast(taux_patronal as float64) as taux_patronal,
    cast(taux_salarial as float64) as taux_salarial,
    cast(montant_total as float64) as montant_total

from source