with evenements as (
    select * from {{ ref('stg_evenements') }}
),

contrats as (
    select * from {{ ref('stg_contrats') }}
),

effectifs as (
    select * from {{ ref('mart_rh__effectifs') }}
),

evenements_avec_contexte as (
    select
        evenements.*,
        contrats.service,
        contrats.csp,
        date_trunc(evenements.date_debut, month) as mois_evenement
    from evenements
    left join contrats
        on evenements.contrat_id = contrats.contrat_id
),

absenteisme_mensuel as (
    select
        mois_evenement as mois,
        service,
        csp,
        type_evenement,
        count(*) as nb_evenements,
        sum(date_diff(date_fin, date_debut, day)) as duree_totale_jours,
        avg(date_diff(date_fin, date_debut, day)) as duree_moyenne_jours
    from evenements_avec_contexte
    group by mois_evenement, service, csp, type_evenement
)

select
    absenteisme_mensuel.mois,
    absenteisme_mensuel.service,
    absenteisme_mensuel.csp,
    absenteisme_mensuel.type_evenement,
    absenteisme_mensuel.nb_evenements,
    absenteisme_mensuel.duree_totale_jours,
    absenteisme_mensuel.duree_moyenne_jours,
    effectifs.effectif,
    round(absenteisme_mensuel.nb_evenements / nullif(effectifs.effectif, 0) * 100, 2) as taux_absenteisme_pct

from absenteisme_mensuel
left join effectifs
    on absenteisme_mensuel.mois = effectifs.mois
    and absenteisme_mensuel.service = effectifs.service
    and absenteisme_mensuel.csp = effectifs.csp

order by absenteisme_mensuel.mois, absenteisme_mensuel.service, absenteisme_mensuel.csp