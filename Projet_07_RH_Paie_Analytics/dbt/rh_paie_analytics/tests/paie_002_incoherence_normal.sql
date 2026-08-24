{{ config(schema='anomalies_metier') }}

with paies_enrichies as (
    select
        paies.matricule,
        paies.mois,
        paies.base,
        paies.montant_total,
        evenements.type_evenement
    from {{ ref('stg_paies') }} as paies
    left join {{ ref('stg_evenements') }} as evenements
        on paies.evenement_id = evenements.evenement_id
)

select
    matricule,
    date_trunc(mois, month) as mois,
    'PAIE_002' as code_anomalie
from paies_enrichies
where (type_evenement is null or type_evenement = 'Congé payé')
  and abs(montant_total - base) / base > 0.05