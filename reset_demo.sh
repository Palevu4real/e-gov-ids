#!/bin/bash
echo "Resetting database and Kafka..."
docker compose restart backend detection-engine
docker compose exec postgres psql -U ids_user -d ids_db -c "DELETE FROM alerts;"
docker compose exec detection-engine rm -f /pcaps/sample.pcap /pcaps/sample.pcap.done
echo "System reset. Generate new PCAPs to trigger alerts."