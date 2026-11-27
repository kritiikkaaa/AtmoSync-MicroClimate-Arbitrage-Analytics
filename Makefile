.PHONY: test simulate dry-run dashboard dbt-compile

test:
	@PYTHONPATH=src python3 -m unittest discover -s tests -v

simulate:
	@PYTHONPATH=src python3 -m atmosync.simulation.sensor_simulator --count 10 --interval-seconds 0

dry-run:
	@PYTHONPATH=src python3 -m atmosync.streaming.kafka_producer --dry-run --count 10 --interval-seconds 0

dashboard:
	@PYTHONPATH=src python3 -m atmosync.dashboard.server

dbt-compile:
	cd dbt_atmosync && dbt deps && dbt compile --profiles-dir .
