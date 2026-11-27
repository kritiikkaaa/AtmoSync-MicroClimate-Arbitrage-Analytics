{{ config(materialized='view') }}

with raw_telemetry as (
    select
        event_id,
        payload,
        kafka_topic,
        kafka_partition,
        kafka_offset,
        ingested_at
    from {{ source('raw', 'raw_iot_telemetry') }}
    qualify row_number() over (partition by event_id order by ingested_at desc) = 1
),

typed as (
    select
        event_id,
        try_to_timestamp_tz(payload:event_ts::string) as event_ts,
        payload:container_id::string as container_id,
        payload:route_id::string as route_id,
        lower(payload:commodity::string) as commodity,
        payload:origin::string as origin,
        payload:destination_market::string as destination_market,
        try_to_decimal(payload:latitude::string, 10, 6) as latitude,
        try_to_decimal(payload:longitude::string, 10, 6) as longitude,
        try_to_decimal(payload:telemetry:temperature_c::string, 8, 2) as temperature_c,
        try_to_decimal(payload:telemetry:humidity_pct::string, 8, 2) as humidity_pct,
        try_to_decimal(payload:telemetry:vibration_g::string, 8, 3) as vibration_g,
        kafka_topic,
        kafka_partition,
        kafka_offset,
        ingested_at
    from raw_telemetry
    where payload:schema_version::string = '1.0'
)

select *
from typed
where event_ts is not null
  and container_id is not null
  and temperature_c between -30 and 30
  and humidity_pct between 0 and 100
  and vibration_g between 0 and 5
