{{ config(materialized='view') }}

select
    price_date,
    lower(commodity) as commodity,
    market,
    market_price_inr_per_kg,
    currency
from {{ ref('commodity_prices') }}
where market_price_inr_per_kg > 0
