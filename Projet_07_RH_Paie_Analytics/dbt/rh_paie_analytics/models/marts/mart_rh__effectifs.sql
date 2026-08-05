with effectif_mensuel as (
    select * from {{ ref('int_effectif_mensuel') }}
),

effectif_total_mensuel as (
    select
        mois,
        sum(effectif) as effectif_total
    from effectif_mensuel
    group by mois
)

select
    effectif_mensuel.mois,
    effectif_mensuel.service,
    effectif_mensuel.csp,
    effectif_mensuel.effectif,
    effectif_total_mensuel.effectif_total

from effectif_mensuel
left join effectif_total_mensuel
    on effectif_mensuel.mois = effectif_total_mensuel.mois

order by effectif_mensuel.mois, effectif_mensuel.service, effectif_mensuel.csp