with paies as (
    select * from {{ ref('stg_paies') }}
),

contrats as (
    select * from {{ ref('stg_contrats') }}
),

paies_avec_contexte as (
    select
        paies.*,
        contrats.service,
        contrats.csp
    from paies
    left join contrats
        on paies.contrat_id = contrats.contrat_id
),

masse_salariale_mensuelle as (
    select
        mois,
        service,
        csp,
        count(distinct matricule) as nb_salaries,
        sum(montant_total) as montant_total_verse,
        sum(taux_patronal) as total_cotisations_patronales,
        sum(taux_salarial) as total_cotisations_salariales,
        round(avg(montant_total), 2) as montant_moyen

    from paies_avec_contexte
    group by mois, service, csp
)

select
    mois,
    service,
    csp,
    nb_salaries,
    montant_total_verse,
    total_cotisations_patronales,
    total_cotisations_salariales,
    montant_moyen

from masse_salariale_mensuelle

order by mois, service, csp