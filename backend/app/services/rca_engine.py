import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.models.rca_model import RCAIncidentModel
from app.schemas.rca_schema import (
    RCAInvestigationRequest,
    RCAReportSchema,
    RCACompareRequest,
    RCACompareResponse
)
from app.services.evidence_collector import EvidenceCollector
from app.services.temporal_analyzer import TemporalAnalyzer
from app.services.dependency_analyzer import DependencyAnalyzer
from app.services.candidate_ranker import CandidateRanker
from app.services.alternative_hypothesis import AlternativeHypothesisEngine
from app.services.diagnostic_recommender import DiagnosticRecommender
from app.services.explanation_builder import ExplanationBuilder
from app.database.rca_repository import RCARepository

logger = logging.getLogger("cascadeshield.rca_engine")

class RCAEngine:
    @staticmethod
    def analyze_incident(
        db: Session,
        request: RCAInvestigationRequest,
        existing_incident_id: Optional[str] = None
    ) -> RCAReportSchema:
        """
        Executes complete, evidence-grounded Root Cause Analysis investigation:
        1. Collects multi-source evidence across Modules 1, 2, and 3.
        2. Performs temporal onset and precedence analysis.
        3. Traverses NetworkX dependency topology.
        4. Ranks candidate root causes using multi-factor deterministic scoring.
        5. Formulates alternative hypotheses.
        6. Generates targeted diagnostic checks.
        7. Synthesizes an auditable investigation report.
        8. Persists findings into SQLite.
        """
        # Fetch digital twin baseline
        services = db.query(ServiceModel).all()
        dependencies = db.query(DependencyModel).all()

        if not services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No services found in Digital Twin. Ensure database is initialized."
            )

        # Determine target and affected services
        target_id = request.target_service_id
        affected_ids = list(request.affected_service_ids or [])

        # If target service specified but not in affected, include it
        if target_id and target_id not in affected_ids:
            affected_ids.append(target_id)

        # If no affected services specified, infer from degraded services in digital twin
        if not affected_ids:
            for s in services:
                if s.health_status in ["critical", "warning"]:
                    affected_ids.append(s.id)

        # Title assignment
        title = request.incident_title or (
            f"Investigation: {target_id or 'Cluster-Wide Anomaly'} ({datetime.now(timezone.utc).strftime('%b %d %H:%M')})"
        )

        # 1. Collect Evidence
        evidence_items = EvidenceCollector.collect_evidence(
            db=db,
            affected_service_ids=affected_ids,
            window_start=request.window_start,
            window_end=request.window_end,
            scenario_id=request.scenario_id
        )

        # 2. Build Event Timeline
        timeline_events = TemporalAnalyzer.build_event_timeline(evidence_items)

        # 3. Build Graphs
        G_dep, G_impact = DependencyAnalyzer.build_networkx_graphs(services, dependencies)

        # 4. Rank Candidate Root Causes
        candidates = CandidateRanker.rank_candidates(
            services=services,
            affected_service_ids=affected_ids,
            evidence_items=evidence_items,
            G_impact=G_impact,
            custom_weights=request.custom_weights
        )

        # 5. Alternative Hypotheses
        alternatives = []
        if request.include_alternatives:
            alternatives = AlternativeHypothesisEngine.generate_hypotheses(
                candidates=candidates,
                affected_service_ids=affected_ids,
                services=services,
                G_dep=G_dep,
                evidence_items=evidence_items
            )

        # 6. Diagnostic Recommendations
        recommendations = []
        if request.include_recommendations:
            recommendations = DiagnosticRecommender.generate_recommendations(
                candidates=candidates,
                evidence_items=evidence_items,
                services=services
            )

        # 7. Persist Incident & Components
        if existing_incident_id:
            incident = RCARepository.get_incident_by_id(db, existing_incident_id)
            if not incident:
                raise HTTPException(status_code=404, detail=f"Incident '{existing_incident_id}' not found.")
            incident_id = incident.id
            RCARepository.update_incident_status(db, incident_id, "completed")
        else:
            incident = RCARepository.create_incident(
                db=db,
                title=title,
                affected_service_ids=affected_ids,
                target_service_id=target_id,
                investigation_window_start=request.window_start,
                investigation_window_end=request.window_end,
                scenario_id=request.scenario_id
            )
            incident_id = incident.id

        # Save evidence models
        raw_evidence = [e.model_dump() for e in evidence_items]
        RCARepository.save_evidence_items(db, incident_id, raw_evidence)

        # Save candidate models
        raw_candidates = [c.model_dump() for c in candidates]
        RCARepository.save_candidates(db, incident_id, raw_candidates)

        # 8. Build Investigation Audit Report
        report = ExplanationBuilder.build_report(
            incident_id=incident_id,
            title=title,
            status="completed" if candidates and candidates[0].ranking_score >= 25.0 else "inconclusive",
            affected_service_ids=affected_ids,
            window_start=request.window_start,
            window_end=request.window_end,
            candidates=candidates,
            evidence_items=evidence_items,
            timeline_events=timeline_events,
            alternative_hypotheses=alternatives,
            diagnostic_recommendations=recommendations
        )

        # Save report JSON in SQLite
        RCARepository.save_report(db, incident_id, report.model_dump(mode="json"))

        return report

    @staticmethod
    def reanalyze_incident(
        db: Session,
        incident_id: str
    ) -> RCAReportSchema:
        """
        Re-executes root cause analysis using updated telemetry and alert evidence.
        """
        incident = RCARepository.get_incident_by_id(db, incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

        affected_ids = []
        try:
            affected_ids = json.loads(incident.affected_service_ids)
        except Exception:
            pass

        req = RCAInvestigationRequest(
            incident_title=f"{incident.title} (Reanalyzed)",
            target_service_id=incident.target_service_id,
            affected_service_ids=affected_ids,
            window_start=incident.investigation_window_start,
            window_end=incident.investigation_window_end,
            scenario_id=incident.scenario_id
        )

        return RCAEngine.analyze_incident(db, req, existing_incident_id=incident_id)

    @staticmethod
    def get_incident_report(
        db: Session,
        incident_id: str
    ) -> Optional[RCAReportSchema]:
        rep_model = RCARepository.get_report_by_incident(db, incident_id)
        if not rep_model:
            return None
        try:
            data = json.loads(rep_model.report_json)
            return RCAReportSchema.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to deserialize RCA report JSON: {e}")
            return None

    @staticmethod
    def compare_incidents(
        db: Session,
        request: RCACompareRequest
    ) -> RCACompareResponse:
        """
        Compares multiple incident investigations side-by-side.
        """
        comparisons = []
        notes = []

        if request.incident_ids:
            for inc_id in request.incident_ids:
                rep = RCAEngine.get_incident_report(db, inc_id)
                if rep:
                    top = rep.primary_root_cause
                    comparisons.append({
                        "incident_id": rep.incident_id,
                        "title": rep.title,
                        "status": rep.status,
                        "affected_services": rep.affected_services,
                        "top_candidate": top.service_name if top else "Unknown",
                        "top_candidate_id": top.service_id if top else None,
                        "confidence_label": top.confidence_label if top else "Insufficient",
                        "ranking_score": top.ranking_score if top else 0.0,
                        "evidence_count": rep.evidence_count,
                        "analyzed_at": rep.analyzed_at.isoformat()
                    })

        if request.custom_requests:
            for req in request.custom_requests:
                rep = RCAEngine.analyze_incident(db, req)
                top = rep.primary_root_cause
                comparisons.append({
                    "incident_id": rep.incident_id,
                    "title": rep.title,
                    "status": rep.status,
                    "affected_services": rep.affected_services,
                    "top_candidate": top.service_name if top else "Unknown",
                    "top_candidate_id": top.service_id if top else None,
                    "confidence_label": top.confidence_label if top else "Insufficient",
                    "ranking_score": top.ranking_score if top else 0.0,
                    "evidence_count": rep.evidence_count,
                    "analyzed_at": rep.analyzed_at.isoformat()
                })

        if len(comparisons) >= 2:
            top_candidates = [c["top_candidate"] for c in comparisons]
            if len(set(top_candidates)) == 1:
                notes.append(f"Convergence observed: All compared incidents isolate '{top_candidates[0]}' as the common primary root cause.")
            else:
                notes.append(f"Divergence observed: Compared incidents point to distinct primary failure origins ({', '.join(set(top_candidates))}).")

        return RCACompareResponse(
            compared_count=len(comparisons),
            comparisons=comparisons,
            comparative_analysis=notes
        )
