with source as (
    select * from {{ source('raw', 'raw_contrats') }}
)

select
    cast(id as int64) as contrat_id,
    cast(salarie_id as int64) as matricule,
    cast(date_debut as date) as date_debut,
    safe_cast(date_fin as date) as date_fin,
    csp,
    service,
    temps_travail,
    type_contrat,
    cast(taux_horaire as float64) as taux_horaire

from source