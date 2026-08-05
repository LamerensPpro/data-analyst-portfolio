with evenements as (
    select * from {{ ref('stg_evenements') }}
),

contrats as (
    select * from {{ ref('stg_contrats') }}
),

evenements_avec_contrat as (
    select
        evenements.*,
        contrats.date_debut as date_debut_contrat
    from evenements
    left join contrats
        on evenements.contrat_id = contrats.contrat_id
)

select
    matricule,
    evenement_id,
    type_evenement,
    date_debut as date_debut_evenement,
    date_debut_contrat,
    'Date evenement anterieure a embauche' as type_anomalie,
    'critique' as niveau_criticite
from evenements_avec_contrat
where date_debut < date_debut_contrat