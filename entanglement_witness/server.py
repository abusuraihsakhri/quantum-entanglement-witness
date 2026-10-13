"""
FastAPI REST API Server for Entanglement Witness & Peres-Horodecki PPT Criterion Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import EntanglementCoordinator
from .ppt import analyze_density_matrix, InvalidDensityMatrix

coordinator = EntanglementCoordinator()


def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel

        app = FastAPI(
            title="Entanglement Witness & Peres-Horodecki PPT Criterion Agent",
            description="Evaluates positive partial transpose (PPT) negativity and construct optimal witness operators detecting multipartite entanglement.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class PPTRequest(BaseModel):
            matrix: list[list[Any]]
            dimensions: list[int] = [2, 2]

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "quantum-entanglement-witness", "domain": "Quantum Information", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/ppt")
        def api_ppt(req: PPTRequest):
            try:
                return analyze_density_matrix(req.matrix, req.dimensions)
            except (InvalidDensityMatrix, ValueError, TypeError) as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
