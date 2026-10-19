from typing import Dict, Any, List, Tuple

class ObservationAnalyzer:
    """
    Analyzes raw diagnostic output, synthesizes new evidence,
    updates candidate confidence rankings, and tracks unresolved incident questions.
    """

    @classmethod
    def analyze_observation(
        cls,
        action_id: str,
        execution_result: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        raw = execution_result.get("raw_result", {})
        candidates = [dict(c) for c in current_context.get("candidates", [])]
        target_service = current_context.get("target_service_id")
        unresolved = list(current_context.get("unresolved_questions", []))
        resolved_new = []
        contradictions = []

        # Analyze by action type
        if action_id == "inspect_service_health":
            status = raw.get("status", "HEALTHY").upper()
            err = raw.get("error_rate", 0.0)
            lat = raw.get("latency_ms", 0.0)
            q = f"What is the current health status and error rate of {target_service}?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)

            if status in ["DEGRADED", "CRITICAL"] or err > 1.0 or lat > 200:
                cls._adjust_candidate_score(candidates, target_service, delta=+12.0)
            else:
                cls._adjust_candidate_score(candidates, target_service, delta=-20.0)
                contradictions.append(f"Service {target_service} is healthy with low error rate ({err:.2f}%).")

        elif action_id == "retrieve_anomaly_alerts":
            total_alerts = raw.get("total_alerts", 0)
            q = f"Are there active anomaly alerts recorded for {target_service}?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)

            if total_alerts > 0:
                cls._adjust_candidate_score(candidates, target_service, delta=+15.0)
            else:
                cls._adjust_candidate_score(candidates, target_service, delta=-15.0)
                contradictions.append(f"Zero anomaly alerts found for suspected service {target_service}.")

        elif action_id == "compare_timestamps":
            delta = raw.get("delta_seconds", 0.0)
            q = f"Did {target_service} degrade prior to downstream callers?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)

            if delta > 0:
                cls._adjust_candidate_score(candidates, target_service, delta=+18.0)
            elif delta < 0:
                cls._adjust_candidate_score(candidates, target_service, delta=-25.0)
                contradictions.append(f"Temporal inversion detected: {target_service} degraded AFTER caller.")

        elif action_id == "trace_failure_paths":
            paths = raw.get("propagation_paths", [])
            q = f"Are there valid dependency call paths from {target_service} to affected callers?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)

            if paths:
                cls._adjust_candidate_score(candidates, target_service, delta=+10.0)
            else:
                cls._adjust_candidate_score(candidates, target_service, delta=-18.0)
                contradictions.append(f"No direct or indirect propagation path exists from {target_service}.")

        elif action_id == "inspect_cascade_prediction":
            blast_count = raw.get("blast_radius_count", 0)
            q = f"What is the predicted cascading blast radius if {target_service} fails?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)

            if blast_count > 0:
                cls._adjust_candidate_score(candidates, target_service, delta=+8.0)

        elif action_id == "compare_hypotheses":
            favored = raw.get("favored_candidate")
            q = "Which competing root cause hypothesis has stronger empirical evidence?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)

            if favored:
                cls._adjust_candidate_score(candidates, favored, delta=+12.0)

        elif action_id == "identify_missing_evidence":
            missing = raw.get("missing_channels", [])
            q = f"What unmonitored observability gaps exist for {target_service}?"
            if q in unresolved:
                unresolved.remove(q)
                resolved_new.append(q)
            # Surfaces observability blind spots
            unresolved.extend([f"Unverified: {m}" for m in missing[:2] if f"Unverified: {m}" not in unresolved])

        # Normalize and re-rank candidates
        candidates.sort(key=lambda c: -c.get("score", 0.0))
        for idx, c in enumerate(candidates):
            c["rank"] = idx + 1
            score = c.get("score", 0.0)
            if score >= 75:
                c["confidence_label"] = "Strong supporting evidence"
            elif score >= 50:
                c["confidence_label"] = "Moderate supporting evidence"
            elif score >= 30:
                c["confidence_label"] = "Weak supporting evidence"
            else:
                c["confidence_label"] = "Insufficient evidence"

        # Evidence completeness score based on actions executed
        executed = list(current_context.get("executed_action_ids", []))
        if action_id not in executed:
            executed.append(action_id)

        essential_actions = [
            "inspect_service_health", 
            "retrieve_anomaly_alerts", 
            "inspect_dependency", 
            "compare_timestamps"
        ]
        completed_essential = sum(1 for a in essential_actions if a in executed)
        completeness = round(completed_essential / len(essential_actions), 2)

        return {
            "updated_candidates": candidates,
            "unresolved_questions": unresolved,
            "resolved_questions": resolved_new,
            "contradictions": contradictions,
            "evidence_completeness": completeness,
            "new_evidence_count": len(execution_result.get("evidence_created", []))
        }

    @staticmethod
    def _adjust_candidate_score(candidates: List[Dict[str, Any]], service_id: Optional[str], delta: float):
        if not service_id:
            return
        for c in candidates:
            if c.get("service_id") == service_id:
                curr = c.get("score", 50.0)
                c["score"] = round(max(0.0, min(100.0, curr + delta)), 1)
                return
        # If candidate not present yet, create it
        if delta > 0:
            candidates.append({
                "service_id": service_id,
                "service_name": service_id,
                "rank": len(candidates) + 1,
                "score": round(max(0.0, min(100.0, 50.0 + delta)), 1),
                "confidence_label": "Moderate supporting evidence"
            })
