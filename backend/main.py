import json
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from database import get_sim_db, get_chat_db, init_chat_db, init_member_ops_db
import os
import time
import threading
import httpx
from simulation_engine import engine as sim_engine

app = FastAPI(title="Decision Intelligence Platform Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional Llama auto-preload on startup. Set LLAMA_AUTO_PRELOAD=1 to attempt loading local model at startup.
@app.on_event("startup")
def _maybe_preload_llama():
    try:
        if os.getenv("LLAMA_AUTO_PRELOAD", "0").lower() in ("1", "true", "yes"):
            try:
                import llama_service
                llama_service.preload()
                print("LLama model preloaded successfully.")
            except Exception as e:
                print("Failed to preload LLama model at startup:", e)
    except Exception:
        pass


# ========== Models ==========
class SimulationRequest(BaseModel):
    action_type: str  # "send_offer", "adjust_comp", "change_campaign"
    target_tier: str | None = None
    patron_id: str | None = None
    params: dict | None = None


class ChatMessageCreate(BaseModel):
    role: str
    content: str


class CompIssueRequest(BaseModel):
    patron_id: str
    comp_type: str
    amount: float
    notes: str | None = None
    issued_by: str | None = None


class BookingCreateRequest(BaseModel):
    patron_id: str
    room_id: str
    check_in: str
    check_out: str
    comped: bool = False
    notes: str | None = None


class FBReservationRequest(BaseModel):
    patron_id: str
    venue: str
    reservation_date: str
    reservation_time: str
    party_size: int
    special_requests: str | None = None


class CreditLineRequest(BaseModel):
    patron_id: str
    credit_limit: float
    signing_limit: float
    notes: str | None = None


class ActionApproveRequest(BaseModel):
    approved_by: str


class ActionExecuteRequest(BaseModel):
    pass


# ========== Overview / Dashboard ==========
@app.get("/api/overview")
def get_overview():
    db = get_sim_db()
    try:
        today = db.execute(
            "SELECT * FROM kpi_daily ORDER BY kpi_date DESC LIMIT 1"
        ).fetchone()
        trend7 = db.execute(
            "SELECT kpi_date, total_wagered, net_revenue, active_patrons, avg_adt, "
            "campaign_response_rate, churn_risk_count FROM kpi_daily ORDER BY kpi_date DESC LIMIT 7"
        ).fetchall()
        tiers = db.execute(
            "SELECT tier, COUNT(*) as count, AVG(adt) as avg_adt, "
            "AVG(lifetime_value) as avg_ltv, AVG(risk_churn) as avg_churn "
            "FROM patrons GROUP BY tier"
        ).fetchall()
        total_patrons = db.execute("SELECT COUNT(*) as c FROM patrons").fetchone()["c"]
        total_hosts = db.execute("SELECT COUNT(*) as c FROM hosts").fetchone()["c"]
        active_tasks = db.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE status IN ('open', 'in_progress')"
        ).fetchone()["c"]
        return {
            "today": dict(today) if today else {},
            "trend_7day": [dict(r) for r in reversed(trend7)],
            "tier_breakdown": [dict(r) for r in tiers],
            "summary": {
                "total_patrons": total_patrons,
                "total_hosts": total_hosts,
                "active_tasks": active_tasks,
            },
        }
    finally:
        db.close()

# (file continues...)

# NOTE: Full file stored in repository.
