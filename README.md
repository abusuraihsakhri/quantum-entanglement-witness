# Quantum Entanglement Witness

> **Domain:** Post-Quantum Cryptography & Zero-Knowledge Architecture
> **Standards:** NIST FIPS 203/204/205, NIST SP 800-90B, ISO/IEC Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

Quantum Entanglement Witness is an enterprise-grade analytical platform that evaluates quantum cryptographic tasks using specialized worker agents. It provides:

- **Multi-agent consensus evaluation** with specialized workers for invariant QC, safety escalation, and protocol conformance
- **Zero-PHI outbound guard** that blocks sensitive identifiers (SSNs, MRNs, phone numbers, emails) from leaving the system
- **Tamper-evident HMAC-SHA256 audit trail** with chained cryptographic signatures
- **FastAPI REST API** with health, metrics, and audit endpoints
- **Peres-Horodecki PPT Criterion** engine for entanglement witness calculations

---

## Architecture

```
quantum-entanglement-witness/
├── agents/                          # Enterprise analytical suite
│   ├── base.py                      # PHI guard, audit trail, security
│   ├── models.py                    # Pydantic v2 data models
│   ├── workers.py                   # Specialized evaluation workers
│   ├── supervisor.py                # Multi-agent orchestrator
│   ├── api.py                       # FastAPI REST endpoints
│   ├── llm_factory.py               # LLM provider abstraction
│   ├── learning.py                  # Bayesian calibration engine
│   ├── metrics.py                   # Prometheus metrics exporter
│   └── streamer.py                  # WebSocket telemetry broadcaster
├── entanglement_witness/             # Peres-Horodecki PPT criterion agent
│   ├── models.py                    # Frontier data models
│   ├── agents.py                    # Sub-agents and coordinator
│   ├── engine.py                    # Core algorithmic engine
│   ├── cli.py                       # CLI for PPT criterion agent
│   └── server.py                    # FastAPI server for PPT agent
├── tests/                           # Test suite
├── web/                             # Operations console (HTML)
├── cli.py                           # Main CLI entry point
├── enrichment.py                    # Domain enrichment engines
├── simulator.py                     # High-throughput stress testing
├── docker-compose.yml               # Container orchestration
└── pyproject.toml                   # Project configuration
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/quantum-entanglement-witness.git
cd quantum-entanglement-witness

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Copy environment template and configure
cp .env.example .env
# Edit .env and set AUDIT_SECRET_KEY to a secure random value
```

### Environment Variables

| Variable | Description | Required |
|:---------|:------------|:---------|
| `AUDIT_SECRET_KEY` | HMAC-SHA256 audit signing key (min 16 chars) | Yes |
| `MODEL_PROVIDER` | LLM provider: `mock`, `ollama`, `claude`, `openai` | No (default: `mock`) |

---

## CLI Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 6. Run Simulation Benchmark
```bash
python simulator.py 1000
```

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/health` | Health check and system metadata |
| `GET` | `/metrics` | Prometheus operational metrics |
| `POST` | `/api/audit` | Submit task for multi-agent evaluation |
| `POST` | `/api/chat` | Supervisory conversational query |
| `GET` | `/api/audit/logs` | Retrieve HMAC-signed audit trail |

### Example API Request
```bash
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=entanglement_witness
```

---

## Security Features

- **Zero-PHI Outbound Interceptor:** AST and regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
- **Path Traversal Protection:** Safe file path resolution for batch operations
- **Configurable Secret Management:** Environment-based key configuration (no hardcoded defaults)

---

## Docker Deployment

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Manual build and run
docker build -t quantum-entanglement-witness .
docker run -p 8000:8000 --env-file .env quantum-entanglement-witness
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
