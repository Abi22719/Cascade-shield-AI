import pytest
from app.services.recovery_risk_service import RecoveryRiskService
from app.services.graph_service import GraphService
from app.schemas.recovery_schemas import (
    RecoveryActionCreate, 
    RecoveryPreconditionSchema, 
    RecoveryConfigSchema
)

def test_risk_score_low_for_safe_actions(db_session):
    actions = [
        RecoveryActionCreate(
            action_type="retry_request",
            target_service_id="srv-notify",
            action_order=1,
            estimated_duration=1,
            reversibility="fully_reversible",
            preconditions=[RecoveryPreconditionSchema(name="Safe", description="Safe", status="satisfied")]
        )
    ]
    G_dep = GraphService.get_dependency_graph(db_session)
    res = RecoveryRiskService.calculate_plan_risk(actions, G_dep=G_dep)

    assert res["risk_score"] < 40.0
    assert res["risk_level"] in ["Low", "Moderate"]
    assert res["reversibility"] == "fully_reversible"
    assert len(res["breakdown"]) == 6

def test_risk_score_high_for_critical_irreversible_actions(db_session):
    actions = [
        RecoveryActionCreate(
            action_type="restore_database",
            target_service_id="srv-database",
            action_order=1,
            estimated_duration=5,
            reversibility="irreversible",
            preconditions=[
                RecoveryPreconditionSchema(name="Backup Verified", description="Verified", status="unresolved")
            ]
        )
    ]
    G_dep = GraphService.get_dependency_graph(db_session)
    res = RecoveryRiskService.calculate_plan_risk(actions, G_dep=G_dep)

    assert res["risk_score"] >= 50.0
    assert res["risk_level"] in ["High", "Critical"]
    assert res["reversibility"] == "irreversible"
    assert res["data_loss_exposure"] == "High"
    assert res["unresolved_preconditions_count"] == 1

def test_risk_score_factors_breakdown(db_session):
    actions = [
        RecoveryActionCreate(
            action_type="traffic_reroute",
            target_service_id="srv-payment",
            action_order=1,
            estimated_duration=2,
            reversibility="fully_reversible"
        )
    ]
    res = RecoveryRiskService.calculate_plan_risk(actions)
    factor_names = [f["factor_name"] for f in res["breakdown"]]
    assert "Service Criticality" in factor_names
    assert "Downstream Blast Radius" in factor_names
    assert "Recovery Duration" in factor_names
    assert "Resource Cost" in factor_names
    assert "Reversibility & Data Loss" in factor_names
    assert "Precondition Uncertainty" in factor_names
