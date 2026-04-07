#!/bin/bash
set -e

COMPOSE_CMD="docker compose"

echo ""
echo "=========================================="
echo "   Data Playground - Setup"
echo "=========================================="
echo ""

# ---------------------------------------------------------------------------
# Wait helpers
# ---------------------------------------------------------------------------

wait_for_polaris() {
    echo "Waiting for Polaris..."
    until curl -sf \
        -X POST http://localhost:8181/api/catalog/v1/oauth/tokens \
        -d "grant_type=client_credentials&client_id=root&client_secret=s3cr3t&scope=PRINCIPAL_ROLE:ALL" \
        2>/dev/null | grep -q "access_token"; do
        printf "."
        sleep 3
    done
    echo " ready"
}

wait_for_trino() {
    echo "Waiting for Trino..."
    until curl -sf http://localhost:8080/v1/info 2>/dev/null | grep -q '"starting":false'; do
        printf "."
        sleep 3
    done
    echo " ready"
}

# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

echo "[1/6] Waiting for services..."
wait_for_polaris
wait_for_trino

echo ""
echo "[2/6] Initializing Polaris catalog..."
$COMPOSE_CMD exec -T dbt python3 /scripts/init_polaris.py

echo ""
echo "[3/6] Initializing MinIO bucket..."
$COMPOSE_CMD exec -T dbt python3 /scripts/init_minio.py

echo ""
echo "[4/6] Loading Iceberg seed data (events)..."
$COMPOSE_CMD exec -T dbt dbt seed --target dev --select iceberg

echo ""
echo "[5/6] Compiling dbt project (generates manifest.json for Dagster)..."
$COMPOSE_CMD exec -T dbt dbt compile --target dev

echo ""
echo "[6/6] Running dbt models..."
$COMPOSE_CMD exec -T dbt dbt run

echo ""
echo "Generating dbt docs..."
$COMPOSE_CMD exec -T dbt dbt docs generate

echo ""
echo "Restarting Dagster to load the dbt manifest..."
$COMPOSE_CMD restart dagster

echo ""
echo "=========================================="
echo "   Setup Complete!"
echo ""
echo "   Dagster UI  -> http://localhost:3000"
echo "   dbt Docs    -> http://localhost:8081"
echo "   MinIO       -> http://localhost:9001"
echo "   Trino       -> http://localhost:8080"
echo "=========================================="
echo ""
echo "Go to http://localhost:3000 and run 'run_dbt_job' to trigger the pipeline."
echo ""
