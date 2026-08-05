with contrats as (
    select * from {{ ref('stg_contrats') }}
),

calendrier as (
    select distinct mois from {{ ref('stg_smic_historique') }}
),

effectif_croise as (
    select
        calendrier.mois,
        contrats.matricule,
        contrats.service,
        contrats.csp
    from calendrier
    inner join contrats
        on calendrier.mois >= date_trunc(contrats.date_debut, month)
        and (
            contrats.date_fin is null
            or calendrier.mois <= date_trunc(contrats.date_fin, month)
        )
)

select
    mois,
    service,
    csp,
    count(distinct matricule) as effectif

from effectif_croise
group by mois, service, csp