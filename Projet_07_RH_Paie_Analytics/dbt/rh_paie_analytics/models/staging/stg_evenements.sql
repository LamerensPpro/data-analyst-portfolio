with source as (
    select * from {{ source('raw', 'raw_evenements') }}
)

select
    cast(id as int64) as evenement_id,
    cast(salarie_id as int64) as matricule,
    cast(contrat_id as int64) as contrat_id,
    type_evenement,
    cast(date_debut as date) as date_debut,
    cast(date_fin as date) as date_fin

from source