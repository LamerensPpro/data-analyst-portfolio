{{ config(schema='anomalies_metier') }}


select
    matricule,
    cast(null as date) as mois,
    'RH_001' as code_anomalie
from {{ ref('stg_salaries') }}
where
    (genre = 'H' and substr(numero_secu, 1, 1) != '1')
    or (genre = 'F' and substr(numero_secu, 1, 1) != '2')