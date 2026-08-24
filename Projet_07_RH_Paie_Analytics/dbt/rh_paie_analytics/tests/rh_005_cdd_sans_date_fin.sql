{{ config(schema='anomalies_metier') }}

select
    matricule,
    date_trunc(date_debut, month) as mois,
    'RH_005' as code_anomalie
from {{ ref('stg_contrats') }}
where type_contrat = 'CDD' and date_fin is null
