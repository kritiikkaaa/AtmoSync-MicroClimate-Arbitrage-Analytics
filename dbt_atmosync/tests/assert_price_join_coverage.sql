-- Week 2 completeness check: telemetry mapped to a supplied price date should
-- carry its market price. Rows outside the limited mock seed date range are allowed.
with telemetry as (
    select * from {{ ref('stg_iot_telemetry') }}
),
available_price_dates as (
    select distinct price_date from {{ ref('stg_commodity_prices') }}
),
enriched as (
    select * from {{ ref('int_container_telemetry_enriched') }}
)

select enriched.*
from enriched
inner join telemetry using (event_id)
inner join available_price_dates
    on to_date(telemetry.event_ts) = available_price_dates.price_date
where enriched.market_price_inr_per_kg is null
