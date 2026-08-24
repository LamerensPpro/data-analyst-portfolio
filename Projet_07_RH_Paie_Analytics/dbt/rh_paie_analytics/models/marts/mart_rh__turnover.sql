with mouvements as (
    select * from {{ ref('int_mouvements_mensuel') }}
),

effectifs as (
    select
        mois,
        sum(effectif) as effectif_total
    from {{ ref('mart_rh__effectifs') }}
    group by mois
)

select
    mouvements.mois,
    mouvements.nb_entrees,
    mouvements.nb_sorties,
    effectifs.effectif_total

from mouvements
left join effectifs
    on mouvements.mois = effectifs.mois

order by mouvements.mois