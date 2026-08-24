{{ config(schema='anomalies_metier') }}

with paies_enrichies as (
    select
        paies.matricule,
        paies.mois,
        paies.base,
        paies.montant_total,
        evenements.date_debut as date_debut_evt,
        evenements.date_fin as date_fin_evt
    from {{ ref('stg_paies') }} as paies
    inner join {{ ref('stg_evenements') }} as evenements
        on paies.evenement_id = evenements.evenement_id
    where evenements.type_evenement = 'Arrêt maladie'
),

montant_attendu as (
    select
        *,
        case
            when date_diff(date_fin_evt, date_debut_evt, day) <= 30 then round(base * 0.90, 2)
            else round(base * 0.6667, 2)
        end as montant_theorique
    from paies_enrichies
)

select
    matricule,
    date_trunc(mois, month) as mois,
    'PAIE_003' as code_anomalie
from montant_attendu
where abs(montant_total - montant_theorique) / montant_theorique > 0.05