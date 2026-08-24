{{ config(schema='anomalies_metier') }}

with paies_enrichies as (
    select
        paies.matricule,
        paies.mois,
        paies.base,
        paies.montant_total
    from {{ ref('stg_paies') }} as paies
    inner join {{ ref('stg_evenements') }} as evenements
        on paies.evenement_id = evenements.evenement_id
    where evenements.type_evenement in ('Congé maternité', 'Congé paternité')
)

select
    matricule,
    date_trunc(mois, month) as mois,
    'PAIE_004' as code_anomalie
from paies_enrichies
where abs(montant_total - round(base * 0.5, 2)) / (base * 0.5) > 0.05