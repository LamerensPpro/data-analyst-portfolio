with paies as (
    select * from {{ ref('stg_paies') }}
),

smic as (
    select * from {{ ref('stg_smic_historique') }}
),

paies_avec_smic as (
    select
        paies.*,
        smic.smic_horaire
    from paies
    left join smic
        on date_trunc(paies.mois, month) = date_trunc(smic.mois, month)
),

anomalie_conversion as (
    select
        matricule,
        paie_id,
        mois,
        montant_total,
        'Conversion horaire vers mensuel manquante' as type_anomalie,
        'critique' as niveau_criticite
    from paies_avec_smic
    where montant_total < 100  -- montant anormalement bas, cohérent avec un taux horaire brut oublié
),

anomalie_sous_smic as (
    select
        matricule,
        paie_id,
        mois,
        montant_total,
        'Salaire sous le SMIC en vigueur' as type_anomalie,
        'critique' as niveau_criticite
    from paies_avec_smic
    where montant_total < (smic_horaire * 151.67 * 0.95)
      and montant_total >= 100
),

anomalie_montant_incoherent as (
    select
        matricule,
        paie_id,
        mois,
        montant_total,
        'Incoherence base x taux vs montant' as type_anomalie,
        'a verifier' as niveau_criticite
    from paies_avec_smic
    where abs(montant_total - (base)) / base > 0.05  -- écart de plus de 5% par rapport à la base attendue
)

select * from anomalie_conversion
union all
select * from anomalie_sous_smic
union all
select * from anomalie_montant_incoherent