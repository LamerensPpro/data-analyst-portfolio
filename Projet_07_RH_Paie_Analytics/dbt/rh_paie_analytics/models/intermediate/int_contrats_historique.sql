with contrats as (
    select * from {{ ref('stg_contrats') }}
),

contrats_ordonnes as (
    select
        *,
        row_number() over (partition by matricule order by date_debut) as rang_contrat,
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
        end as ordre_csp_actuel,
        case csp_precedente
            when 'Employé' then 0
            when 'Agent de maîtrise' then 1
            when 'Cadre' then 2
        end as ordre_csp_precedent
    from contrats_ordonnes
)

select
    matricule,
    contrat_id,
    date_debut,
    csp_precedente,
    csp as csp_actuelle,
    'Rétrogradation CSP' as type_anomalie,
    'a verifier' as niveau_criticite
from ordre_csp
where ordre_csp_precedent is not null
  and ordre_csp_actuel < ordre_csp_precedent