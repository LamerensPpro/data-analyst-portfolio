with source as (
    select * from {{ source('raw', 'raw_salaries') }}
)

select
    cast(id as int64) as matricule,
    nom,
    prenom,
    genre,
    cast(date_naissance as date) as date_naissance,
    cast(numero_secu as string) as numero_secu,
    cast(date_embauche as date) as date_embauche

from source