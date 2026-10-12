down:
	docker compose --env-file .env.main down -v --remove-orphans

clean:
	docker compose --env-file .env.main rm --stop --volumes --force

up: down clean
	docker compose --env-file .env.main up --build -V

up-processor-success: down clean
	docker compose --env-file .env.main --env-file .env.success up --build -V

up-processor-error: down clean
	docker compose --env-file .env.main --env-file .env.error up --build -V


create-normal-1:
	curl -v \
		-X POST \
		-H "X-API-Key: test" \
		-H "Idempotency-Key: normal-1" \
		-H "Content-Type: application/json" \
		--data @payloads/normal-1.json \
		http://localhost:8080/api/v1/payments

create-normal-2:
	curl -v \
		-X POST \
		-H "X-API-Key: test" \
		-H "Idempotency-Key: normal-2" \
		-H "Content-Type: application/json" \
		--data @payloads/normal-2.json \
		http://localhost:8080/api/v1/payments

create-invalid-webhook:
	curl -v \
		-X POST \
		-H "X-API-Key: test" \
		-H "Idempotency-Key: invalid-webhook" \
		-H "Content-Type: application/json" \
		--data @payloads/invalid-webhook.json \
		http://localhost:8080/api/v1/payments
