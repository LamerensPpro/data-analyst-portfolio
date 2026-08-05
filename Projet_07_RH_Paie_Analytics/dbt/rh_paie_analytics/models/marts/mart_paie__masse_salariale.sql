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
),

anomalies_par_mois as (
    select
        mois,
        count(*) as nb_anomalies_paie
    from {{ ref('int_anomalies_paies') }}
    group by mois
)

select
    masse_salariale_mensuelle.mois,
    masse_salariale_mensuelle.service,
    masse_salariale_mensuelle.csp,
    masse_salariale_mensuelle.nb_salaries,
    masse_salariale_mensuelle.montant_total_verse,
    masse_salariale_mensuelle.total_cotisations_patronales,
    masse_salariale_mensuelle.total_cotisations_salariales,
    masse_salariale_mensuelle.montant_moyen,
    anomalies_par_mois.nb_anomalies_paie

from masse_salariale_mensuelle
left join anomalies_par_mois
    on masse_salariale_mensuelle.mois = anomalies_par_mois.mois

order by masse_salariale_mensuelle.mois, masse_salariale_mensuelle.service, masse_salariale_mensuelle.csp