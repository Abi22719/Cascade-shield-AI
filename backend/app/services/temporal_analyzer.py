from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from app.schemas.rca_schema import EvidenceItemSchema, TimelineEventSchema

class TemporalAnalyzer:
    @staticmethod
    def extract_service_earliest_timestamps(
        evidence_items: List[EvidenceItemSchema]
    ) -> Dict[str, datetime]:
        """
        Identifies the earliest observed abnormality timestamp for each service.
        Ignores contradictory evidence when determining onset.
        """
        earliest_map: Dict[str, datetime] = {}
        for ev in evidence_items:
            if ev.is_contradictory or not ev.timestamp:
                continue
            svc_id = ev.service_id
            if svc_id not in earliest_map or ev.timestamp < earliest_map[svc_id]:
                earliest_map[svc_id] = ev.timestamp
        return earliest_map

    @staticmethod
    def evaluate_temporal_precedence(
        candidate_id: str,
        affected_ids: List[str],
        earliest_map: Dict[str, datetime]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Evaluates whether candidate_id degraded BEFORE the affected services.
        Returns:
        - precedence_score (0.0 to 1.0)
        - supporting_statements (evidence for)
        - contradictory_statements (evidence against)
        """
        t_cand = earliest_map.get(candidate_id)
        if not t_cand:
            return 0.5, [], ["No clear timestamp available for candidate onset."]

        supported_count = 0
        inverted_count = 0
        supporting: List[str] = []
        contradictory: List[str] = []

        for aff_id in affected_ids:
            if aff_id == candidate_id:
                continue
            t_aff = earliest_map.get(aff_id)
            if not t_aff:
                continue

            delta_seconds = (t_aff - t_cand).total_seconds()
            if delta_seconds >= 0:
                supported_count += 1
                supporting.append(
                    f"Candidate anomaly preceded affected service '{aff_id}' by {abs(delta_seconds):.1f}s."
                )
            else:
                inverted_count += 1
                contradictory.append(
                    f"Temporal Inversion: Affected service '{aff_id}' degraded {abs(delta_seconds):.1f}s BEFORE candidate '{candidate_id}'."
                )

        total_compared = supported_count + inverted_count
        if total_compared == 0:
            return 0.6, ["Single-point or simultaneous observation window."], []

        score = supported_count / total_compared
        return round(score, 2), supporting, contradictory

    @staticmethod
    def build_event_timeline(
        evidence_items: List[EvidenceItemSchema]
    ) -> List[TimelineEventSchema]:
        """
        Converts collected evidence items into a sorted, human-readable timeline.
        """
        timeline: List[TimelineEventSchema] = []

        # Filter out evidence with no timestamp and sort chronologically
        timestamped = [e for e in evidence_items if e.timestamp]
        timestamped.sort(key=lambda x: x.timestamp)

        for ev in timestamped:
            ts_utc = ev.timestamp if ev.timestamp.tzinfo else ev.timestamp.replace(tzinfo=timezone.utc)
            ts_str = ts_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

            severity = "warning"
            if ev.is_contradictory:
                severity = "info"
            elif "CRITICAL" in ev.evidence_summary.upper() or (ev.observed_value and ev.observed_value >= 90):
                severity = "critical"
            elif "WARNING" in ev.evidence_summary.upper():
                severity = "warning"

            timeline.append(
                TimelineEventSchema(
                    timestamp=ts_utc,
                    timestamp_formatted=ts_str,
                    service_id=ev.service_id,
                    service_name=ev.service_name,
                    event_type=ev.evidence_type,
                    source_module=ev.source_module,
                    description=ev.evidence_summary,
                    severity=severity,
                    evidence_id=ev.id
                )
            )

        return timeline
