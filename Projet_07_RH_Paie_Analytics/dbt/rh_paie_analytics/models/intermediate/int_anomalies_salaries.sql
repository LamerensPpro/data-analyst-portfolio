with salaries as (
    select * from {{ ref('stg_salaries') }}
),

genre_secu_incoherent as (
    select
        matricule,
        'Genre incohérent avec numéro de sécu' as type_anomalie,
        'critique' as niveau_criticite
    from salaries
    where
        (genre = 'H' and substr(numero_secu, 1, 1) != '1')
        or (genre = 'F' and substr(numero_secu, 1, 1) != '2')
),

numero_secu_duplique as (
    select
        matricule,
        'Numéro de sécu dupliqué' as type_anomalie,
        'critique' as niveau_criticite
    from salaries
    where numero_secu in (
        select numero_secu
        from salaries
        group by numero_secu
        having count(*) > 1
    )
)

select * from genre_secu_incoherent
union all
select * from numero_secu_duplique