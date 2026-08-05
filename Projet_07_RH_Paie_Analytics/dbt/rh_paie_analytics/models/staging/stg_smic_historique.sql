with source as (
    select * from {{ source('raw', 'raw_smic_historique') }}
)

select
    cast(mois as date) as mois,
    cast(smic_horaire as float64) as smic_horaire

from source