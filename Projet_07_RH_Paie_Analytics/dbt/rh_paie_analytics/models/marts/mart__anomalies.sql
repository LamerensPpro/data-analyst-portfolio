with anomalies_salaries as (
    select
        matricule,
        cast(null as date) as mois,
        type_anomalie,
        niveau_criticite,
        'RH' as domaine
    from {{ ref('int_anomalies_salaries') }}
),

anomalies_evenements as (
    select
        matricule,
        date_trunc(date_debut_evenement, month) as mois,
        type_anomalie,
        niveau_criticite,
        'RH' as domaine
    from {{ ref('int_anomalies_evenements') }}
),

anomalies_retrogradations as (
    select
        matricule,
        date_trunc(date_debut, month) as mois,
        type_anomalie,
        niveau_criticite,
        'RH' as domaine
    from {{ ref('int_contrats_historique') }}
),

anomalies_paies as (
    select
        matricule,
        date_trunc(mois, month) as mois,
        type_anomalie,
        niveau_criticite,
        'Paie' as domaine
    from {{ ref('int_anomalies_paies') }}
)

select * from anomalies_salaries
union all
select * from anomalies_evenements
union all
select * from anomalies_retrogradations
union all
select * from anomalies_paies