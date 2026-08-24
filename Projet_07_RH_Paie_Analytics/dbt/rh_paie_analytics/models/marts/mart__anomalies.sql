with historique as (
    select * from {{ source('anomalies_metier', 'historique_anomalies') }}
),
ref as (
    select * from {{ ref('ref_anomalies') }}
)
select
    historique.date_run,
    historique.matricule,
    historique.mois,
    historique.code_anomalie,
    ref.libelle as type_anomalie,
    ref.domaine,
    ref.niveau_criticite
from historique
left join ref
    on historique.code_anomalie = ref.code_anomalie