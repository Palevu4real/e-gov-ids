# 🛡️ E-Gov IDS: Intrusion Detection System for E-Governance

A full-stack, microservice-based Intrusion Detection System (IDS) designed to secure e-governance infrastructure. It captures network traffic, detects malicious patterns using signature and anomaly detection, and streams real-time alerts to a secure analyst dashboard.

## 🏗️ Architecture
- **Detection Engine:** Python + Scapy (Packet capture & feature extraction) + Scikit-Learn (Anomaly detection)
- **Message Broker:** Redpanda (Kafka API) for high-throughput event streaming
- **Backend API:** FastAPI + Async SQLAlchemy + JWT Authentication
- **Database:** PostgreSQL (Alerts & Users) + Redis (Caching)
- **Frontend:** React + Vite + TailwindCSS + Recharts

## 🚀 Quick Start (Docker)
Prerequisites: Docker Desktop installed and running.

1. Clone the repository and navigate to the root folder.
2. Create your `.env` file from the example:
   ```bash
   cp .env.example .env

   Generate a secret key and paste it into .env as JWT_SECRET_KEY:
   openssl rand -hex 32

   Boot the entire system:
   docker compose up -d --build

   🖥️ Accessing the System
Frontend Dashboard: http://localhost:5173

Backend API Docs (Swagger): http://localhost:8000/docs

Default Admin Login
Email: admin@gov.example.com

Password: AdminPass123!

🧪 Generating Test Attacks
To see the IDS in action, you can generate a simulated PCAP file containing a Port Scan and a Brute Force attack:

bash
docker compose exec detection-engine python generate_pcap.py
Wait 5 seconds, and the alerts will appear live on your dashboard.

📂 Project Structure
/backend: FastAPI application, models, and Kafka consumer.

/detection-engine: Scapy packet parsing and ML detection logic.

/frontend: React analyst dashboard.

/infra: Deployment configurations.

text

---

### 📄 2. Create `SECURITY.md` (Root Folder)
This directly addresses **Point 4** from your very first prompt (making compliance claims precise). You can put this in your thesis appendix!

```markdown
# Security Controls & Compliance Mapping

This document outlines the security controls implemented in the E-Gov IDS and maps them to standard frameworks (NIST CSF, ISO 27001). 

*Note: The presence of these controls does not constitute automatic certification, but provides the technical evidence required for an audit.*

## 1. Authentication & Access Control
- **Control:** JWT (JSON Web Tokens) with short-lived expiry (60 minutes) and Role-Based Access Control (RBAC).
- **Evidence:** Passwords are hashed using bcrypt. API endpoints enforce token validation.
- **Framework Mapping:** NIST CSF PR.AC-1 (Identities and credentials are managed).

## 2. Data Protection
- **Control:** All API traffic is designed for TLS termination. PII and sensitive alerts are stored in PostgreSQL. 
- **Evidence:** Database schema enforces strict typing. Environment variables are used for secrets (no hardcoded credentials).
- **Framework Mapping:** ISO 27001 A.10.1 (Cryptographic controls).

## 3. Audit Logging
- **Control:** Every alert is timestamped at the database level (`server_default=func.now()`).
- **Evidence:** The `alerts` table provides an immutable record of detections. Future iterations include hash-chaining the audit log.
- **Framework Mapping:** NIST CSF PR.PT-1 (Audit/log records are determined, documented, implemented, and reviewed).

## 4. Real-Time Monitoring (The IDS)
- **Control:** Continuous packet inspection using signature and anomaly detection.
- **Evidence:** Scapy engine publishes to Kafka; FastAPI consumer processes in real-time.
- **Framework Mapping:** ISO 27001 A.12.4 (Event logging and monitoring).
📄 3. The Final "Clean up" Script
If you ever want to demonstrate this to an examiner, you should know how to wipe the database clean and start fresh (so they only see the attacks you generate during the demo).

Create a file in the root called reset_demo.sh:

bash
#!/bin/bash
echo "Resetting database and Kafka..."
docker compose restart backend detection-engine
docker compose exec postgres psql -U ids_user -d ids_db -c "DELETE FROM alerts;"
docker compose exec detection-engine rm -f /pcaps/sample.pcap /pcaps/sample.pcap.done
echo "System reset. Generate new PCAPs to trigger alerts."