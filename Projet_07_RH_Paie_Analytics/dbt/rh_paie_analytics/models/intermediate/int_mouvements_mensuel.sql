with contrats as (
    select * from {{ ref('stg_contrats') }}
),

entrees as (
    select
        date_trunc(date_debut, month) as mois,
        count(*) as nb_entrees
    from contrats
    group by date_trunc(date_debut, month)
),

sorties as (
    select
        date_trunc(date_fin, month) as mois,
        count(*) as nb_sorties
    from contrats
    where date_fin is not null
    group by date_trunc(date_fin, month)
)

select
    coalesce(entrees.mois, sorties.mois) as mois,
    coalesce(entrees.nb_entrees, 0) as nb_entrees,
    coalesce(sorties.nb_sorties, 0) as nb_sorties

from entrees
full outer join sorties
    on entrees.mois = sorties.mois

order by mois