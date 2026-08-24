{{ config(schema='anomalies_metier') }}


with evenements as (
    select * from {{ ref('stg_evenements') }}
),

contrats as (
    select * from {{ ref('stg_contrats') }}
)

select
    evenements.matricule,
    date_trunc(contrats.date_debut, month) as mois,
    'RH_004' as code_anomalie
from evenements
left join contrats
    on evenements.contrat_id = contrats.contrat_id
where evenements.date_debut < contrats.date_debut