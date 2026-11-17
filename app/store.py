"""Local SQLite store for a synthetic, non-production advisory demonstration.

No real client data, authentication, multi-user authorization, or migrations are
implemented here. The database is intended for a local demo only.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


STAGES = (
    "DISCOVER",
    "ASSESS",
    "PRIORITIZE",
    "ARCHITECT",
    "VALIDATE",
    "ADOPT",
    "MEASURE_IMPROVE",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


CLIENTS = (
    (
        "fintrust-demo",
        "FinTrust",
        "Financial services",
        "A fictional financial institution evaluating safe policy answers and approval requests.",
        "FT",
    ),
    (
        "retailflow-demo",
        "RetailFlow",
        "Retail",
        "A fictional retailer exploring operational discrepancy investigation and recommendations.",
        "RF",
    ),
    (
        "civicdata-demo",
        "CivicData",
        "Public sector",
        "A fictional public-sector organization considering trustworthy policy-based services.",
        "CD",
    ),
)

CASES = (
    (
        "fintrust-policy-action", "fintrust-demo", "Policy & Action Assistant",
        "Employees need supported answers about purchasing policies and controlled exception requests.",
        "Fictional procurement sponsor", "Evidence-backed answer rate (not yet measured)",
        "Rule-based decision tree and searchable policy portal", "HIGH",
    ),
    (
        "retailflow-discrepancy", "retailflow-demo", "Operational Discrepancy Investigation",
        "Regional teams want to investigate inconsistent inventory and operational records.",
        "Fictional operations director", "Time to explain a discrepancy (not yet measured)",
        "Existing analytics dashboard with rule-based exception reports", "MEDIUM",
    ),
    (
        "civicdata-policy", "civicdata-demo", "Public Service Policy Navigator",
        "Teams need reliable policy references and must identify unsupported requests.",
        "Fictional service manager", "Supported response rate (not yet measured)",
        "Curated policy search and human service workflow", "HIGH",
    ),
)


class StudioStore:
    """One connection per operation; safe for local FastAPI request handling."""

    def __init__(self, db_path: Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=8.0)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    description TEXT NOT NULL,
                    initials TEXT NOT NULL,
                    synthetic INTEGER NOT NULL CHECK (synthetic = 1)
                );
                CREATE TABLE IF NOT EXISTS use_cases (
                    case_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL REFERENCES clients(client_id),
                    title TEXT NOT NULL,
                    problem TEXT NOT NULL,
                    business_owner TEXT NOT NULL,
                    success_metric TEXT NOT NULL,
                    non_ai_alternative TEXT NOT NULL,
                    risk_tier TEXT NOT NULL CHECK (risk_tier IN ('LOW','MEDIUM','HIGH'))
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL REFERENCES use_cases(case_id),
                    evidence_class TEXT NOT NULL CHECK (evidence_class IN ('DECLARED','DOCUMENTED','MEASURED','INFERRED')),
                    verification_status TEXT NOT NULL CHECK (verification_status IN ('UNVERIFIED','VERIFIED','REJECTED')),
                    source TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_reviews (
                    review_id TEXT PRIMARY KEY,
                    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
                    verification_status TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL REFERENCES use_cases(case_id),
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    evidence_ids_json TEXT NOT NULL,
                    blockers_json TEXT NOT NULL,
                    alternatives_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decision_invalidations (
                    invalidation_id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
                    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
                    review_id TEXT NOT NULL REFERENCES evidence_reviews(review_id),
                    created_at TEXT NOT NULL,
                    UNIQUE(decision_id, review_id)
                );
                CREATE INDEX IF NOT EXISTS evidence_case_idx ON evidence(case_id);
                CREATE INDEX IF NOT EXISTS decision_case_stage_idx ON decisions(case_id, stage, created_at);
                CREATE INDEX IF NOT EXISTS invalidation_decision_idx ON decision_invalidations(decision_id);
                """
            )
            count = conn.execute("SELECT count(*) FROM clients").fetchone()[0]
            if count:
                return
            conn.executemany(
                "INSERT INTO clients VALUES (?, ?, ?, ?, ?, 1)", CLIENTS
            )
            conn.executemany(
                "INSERT INTO use_cases VALUES (?, ?, ?, ?, ?, ?, ?, ?)", CASES
            )
            now = utc_now()
            seed_evidence = (
                ("e-sim-001", "fintrust-policy-action", "DECLARED", "UNVERIFIED", "Synthetic stakeholder interview", "Staff report difficulty locating applicable procurement rules.", now),
                ("e-sim-002", "fintrust-policy-action", "DOCUMENTED", "UNVERIFIED", "Synthetic policy placeholder", "No reviewed policy corpus is available yet; technical validation is pending.", now),
                ("e-sim-003", "retailflow-discrepancy", "DECLARED", "UNVERIFIED", "Synthetic operations scenario", "Regional teams suspect inconsistent inventory information; impact has not been quantified.", now),
                ("e-sim-004", "civicdata-policy", "DOCUMENTED", "UNVERIFIED", "Synthetic policy source description", "The applicable policy versions and authority must still be established.", now),
            )
            conn.executemany("INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?)", seed_evidence)
            conn.execute(
                "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "d-fintrust-001", "fintrust-policy-action", "DISCOVER", "IN_REVIEW",
                    "Fictional advisory reviewer",
                    "Problem identified, but baseline and applicable policy are unverified.",
                    json.dumps(["e-sim-001", "e-sim-002"]),
                    json.dumps(["No measured baseline", "No validated policy corpus"]),
                    json.dumps(["Rule-based decision tree", "Searchable policy portal"]),
                    now,
                ),
            )

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict | None:
        return dict(row) if row is not None else None

    def clients(self) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute(
                """SELECT c.*, count(u.case_id) AS case_count
                   FROM clients c LEFT JOIN use_cases u USING(client_id)
                   GROUP BY c.client_id ORDER BY c.name"""
            ).fetchall()
            return [dict(row) for row in rows]

    def client(self, client_id: str) -> dict | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM clients WHERE client_id=?", (client_id,)).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["use_cases"] = [dict(r) for r in conn.execute(
                "SELECT * FROM use_cases WHERE client_id=? ORDER BY title", (client_id,)
            ).fetchall()]
            return result

    def case(self, case_id: str) -> dict | None:
        with self.connection() as conn:
            row = conn.execute(
                """SELECT u.*, c.name AS client_name, c.sector, c.synthetic
                   FROM use_cases u JOIN clients c USING(client_id) WHERE u.case_id=?""",
                (case_id,),
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["evidence"] = [dict(e) for e in conn.execute(
                "SELECT * FROM evidence WHERE case_id=? ORDER BY created_at, evidence_id", (case_id,)
            ).fetchall()]
            decisions = [dict(d) for d in conn.execute(
                "SELECT * FROM decisions WHERE case_id=? ORDER BY rowid DESC", (case_id,)
            ).fetchall()]
            for d in decisions:
                for key in ("evidence_ids", "blockers", "alternatives"):
                    d[key] = json.loads(d.pop(f"{key}_json"))
            result["decisions"] = decisions
            latest = {}
            for d in decisions:
                latest.setdefault(d["stage"], d)
            invalidations = {r[0] for r in conn.execute(
                "SELECT decision_id FROM decision_invalidations WHERE decision_id IN "
                "(SELECT decision_id FROM decisions WHERE case_id=?)", (case_id,)
            ).fetchall()}
            result["stage_states"] = self._stage_states(
                latest, {item["evidence_id"]: item for item in result["evidence"]}, invalidations
            )
            return result

    @staticmethod
    def _stage_states(latest: dict[str, dict], evidence: dict[str, dict],
                      invalidations: set[str]) -> list[dict]:
        """Derive effective gates without rewriting the human decision history.

        A recorded GO ceases to unlock later stages when its supporting evidence
        is rejected or no longer verified. The original decision remains intact
        and visible for audit; a fresh human review is needed to reopen the gate.
        """
        states = []
        unlocked = True
        for stage in STAGES:
            recorded = latest.get(stage)
            state = recorded["status"] if recorded is not None and unlocked else "LOCKED" if not unlocked else "NOT_STARTED"
            invalidation = None
            if state == "GO":
                references = [evidence.get(identifier) for identifier in recorded["evidence_ids"]]
                has_verified_basis = any(
                    item is not None
                    and item["verification_status"] == "VERIFIED"
                    and item["evidence_class"] in ("DOCUMENTED", "MEASURED")
                    for item in references
                )
                has_measurement = any(
                    item is not None
                    and item["verification_status"] == "VERIFIED"
                    and item["evidence_class"] == "MEASURED"
                    for item in references
                )
                if (recorded["decision_id"] in invalidations or not has_verified_basis
                        or (stage in ("VALIDATE", "MEASURE_IMPROVE") and not has_measurement)):
                    state = "REWORK"
                    invalidation = "The recorded approval lost its supporting evidence; a new human decision is required."
            states.append({
                "stage": stage,
                "status": state,
                "decision": recorded if unlocked else None,
                "invalidation_reason": invalidation,
            })
            unlocked = state == "GO"
        return states

    def evidence(self, evidence_id: str) -> dict | None:
        with self.connection() as conn:
            return self._row(conn.execute("SELECT * FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone())

    def add_evidence(self, case_id: str, evidence_class: str, source: str, summary: str) -> dict:
        new = {
            "evidence_id": f"e-demo-{uuid4().hex[:12]}", "case_id": case_id,
            "evidence_class": evidence_class, "verification_status": "UNVERIFIED",
            "source": source, "summary": summary, "created_at": utc_now(),
        }
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO evidence VALUES (:evidence_id,:case_id,:evidence_class,:verification_status,:source,:summary,:created_at)",
                new,
            )
        return new

    def review_evidence(self, evidence_id: str, status: str, reviewer: str, rationale: str) -> dict:
        with self.connection() as conn:
            review_id = f"er-{uuid4().hex[:12]}"
            case_id = conn.execute(
                "SELECT case_id FROM evidence WHERE evidence_id=?", (evidence_id,)
            ).fetchone()[0]
            conn.execute(
                "UPDATE evidence SET verification_status=? WHERE evidence_id=?",
                (status, evidence_id),
            )
            conn.execute(
                "INSERT INTO evidence_reviews VALUES (?, ?, ?, ?, ?, ?)",
                (review_id, evidence_id, status, reviewer, rationale, utc_now()),
            )
            if status == "REJECTED":
                prior_go = conn.execute(
                    "SELECT decision_id, evidence_ids_json FROM decisions WHERE case_id=? AND status='GO'",
                    (case_id,),
                ).fetchall()
                for decision in prior_go:
                    if evidence_id in json.loads(decision["evidence_ids_json"]):
                        conn.execute(
                            "INSERT INTO decision_invalidations VALUES (?, ?, ?, ?, ?)",
                            (f"di-{uuid4().hex[:12]}", decision["decision_id"], evidence_id, review_id, utc_now()),
                        )
        return self.evidence(evidence_id) or {}

    def add_decision(self, case_id: str, stage: str, status: str, owner: str,
                     rationale: str, evidence_ids: list[str], blockers: list[str],
                     alternatives: list[str]) -> dict:
        record = {
            "decision_id": f"d-demo-{uuid4().hex[:12]}", "case_id": case_id,
            "stage": stage, "status": status, "owner": owner,
            "rationale": rationale, "evidence_ids_json": json.dumps(evidence_ids),
            "blockers_json": json.dumps(blockers),
            "alternatives_json": json.dumps(alternatives), "created_at": utc_now(),
        }
        with self.connection() as conn:
            conn.execute(
                """INSERT INTO decisions VALUES (:decision_id,:case_id,:stage,:status,:owner,:rationale,
                   :evidence_ids_json,:blockers_json,:alternatives_json,:created_at)""", record
            )
        return record
