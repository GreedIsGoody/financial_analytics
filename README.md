# Financial Analytics Service 📈

A high-performance financial analytics backend service built with **FastAPI**, **PostgreSQL**, and **ClickHouse**. It implements the **Transactional Outbox Pattern** to reliably stream financial events between databases, ensuring strict data consistency and fault tolerance.

---

## 🚀 Key Features

* **Transaction Processing:** Fast HTTP endpoints to accept and validate incoming financial transactions.
* **Transactional Outbox Pattern:** Guarantees *at-least-once* event delivery from PostgreSQL to ClickHouse without relying on external message brokers.
* **Analytical Data Store:** High-speed analytical queries powered by ClickHouse.
* **Resilient Relayer Worker:** Background worker with automatic retries, exponential backoff, and graceful shutdown support (`asyncio.CancelledError`).
* **Strict Type Safety:** Data validation using Pydantic v2 and Decimal handling for exact financial accuracy.

---

## 🛠️ Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Relational DB:** PostgreSQL (via SQLAlchemy 2.0 Async)
* **Analytical DB:** ClickHouse
* **Language:** Python 3.11+
* **Containerization:** Docker & Docker Compose

---

## 🏗️ Architecture Overview

1. **API Layer:** Client submits a transaction (`POST /transactions`).
2. **PostgreSQL Write:** The transaction data and an `OutboxEvent` (`processed = false`) are saved within a single database transaction.
3. **Outbox Relayer Worker:** Background task polls pending outbox events, formats them, and batches writes into **ClickHouse**.
4. **Status Update:** Upon successful insert, events in PostgreSQL are marked as `processed = true`.

---

## 🚦 Quick Start

### 1. Clone the repository
```bash
git clone [https://github.com/GreedIsGoody/financial_analytics.git](https://github.com/GreedIsGoody/financial_analytics.git)
cd financial_analytics
```

### 2. Set up Environment Variables
Create a .env file in the root directory:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=financial_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DB=default
### 3. Run with Docker Compose

docker-compose up -d --build

### 4. Interactive API Docs
Once running, open your browser and head to:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc