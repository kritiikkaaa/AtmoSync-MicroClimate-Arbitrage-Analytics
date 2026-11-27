{{ config(materialized='view') }}

with telemetry as (
    select * from {{ ref('stg_iot_telemetry') }}
),

prices as (
    select * from {{ ref('stg_commodity_prices') }}
)

select
    telemetry.event_id,
    telemetry.event_ts,
    telemetry.container_id,
    telemetry.route_id,
    telemetry.commodity,
    telemetry.origin,
    telemetry.destination_market,
    telemetry.latitude,
    telemetry.longitude,
    telemetry.temperature_c,
    telemetry.humidity_pct,
    telemetry.vibration_g,
    prices.market_price_inr_per_kg,
    prices.currency,
    case
        when telemetry.temperature_c > 7 then 'above_cold_chain_target'
        when telemetry.temperature_c < 2 then 'below_cold_chain_target'
        else 'within_baseline_range'
    end as temperature_status,
    telemetry.kafka_topic,
    telemetry.kafka_partition,
    telemetry.kafka_offset,
    telemetry.ingested_at
from telemetry
left join prices
    on telemetry.commodity = prices.commodity
    and telemetry.destination_market = prices.market
    and to_date(telemetry.event_ts) = prices.price_date
