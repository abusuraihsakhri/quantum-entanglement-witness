"""
FastAPI REST API Server for Quantum Entanglement Witness.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from entanglement_witness.ppt import analyze_density_matrix, InvalidDensityMatrix

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Quantum Entanglement Witness API",
    description="PPT analysis plus legacy threshold-based telemetry",
    version="2.1.0",
)


class PPTRequest(BaseModel):
    matrix: List[List[Any]]
    dimensions: List[int] = [2, 2]


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "quantum-entanglement-witness", "domain": "Quantum information / legacy telemetry", "standard": "Peres–Horodecki PPT (for /api/ppt)", "version": "2.1.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


@app.post("/api/ppt")
def api_ppt(request: PPTRequest):
    """Compute PPT spectra, negativity and an NPT witness for 2x2 or 2x3."""
    try:
        return analyze_density_matrix(request.matrix, request.dimensions)
    except (InvalidDensityMatrix, ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
