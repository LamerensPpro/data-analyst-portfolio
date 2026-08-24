{{ config(schema='anomalies_metier') }}


with contrats as (
    select * from {{ ref('stg_contrats') }}
),

contrats_ordonnes as (
    select
        *,
        lag(csp) over (partition by matricule order by date_debut) as csp_precedente
    from contrats
),

ordre_csp as (
    select
        *,
        case csp
            when 'Employé' then 0
            when 'Agent de maîtrise' then 1
            when 'Cadre' then 2
        end as ordre_actuel,
        case csp_precedente
            when 'Employé' then 0
            when 'Agent de maîtrise' then 1
            when 'Cadre' then 2
        end as ordre_precedent
    from contrats_ordonnes
)

select
    matricule,
    date_trunc(date_debut, month) as mois,
    'RH_003' as code_anomalie
from ordre_csp
where ordre_precedent is not null
  and ordre_actuel < ordre_precedent