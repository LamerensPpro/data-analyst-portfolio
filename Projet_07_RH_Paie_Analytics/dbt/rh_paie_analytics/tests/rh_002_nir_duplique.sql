{{ config(schema='anomalies_metier') }}


select
    matricule,
    cast(null as date) as mois,
    'RH_002' as code_anomalie
from {{ ref('stg_salaries') }}
where numero_secu in (
    select numero_secu
    from {{ ref('stg_salaries') }}
    group by numero_secu
    having count(*) > 1
)