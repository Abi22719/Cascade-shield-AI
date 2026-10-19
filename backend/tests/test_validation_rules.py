import pytest
from app.services.validation_rules import ValidationRuleEngine, DEFAULT_VALIDATION_CONFIG

def test_validation_rule_defaults(db_session):
    cfg = ValidationRuleEngine.get_config(db_session)
    assert cfg.max_acceptable_latency_ms == 500.0
    assert cfg.max_acceptable_error_rate == 5.0
    assert cfg.verification_window_steps == 3
    assert "srv-database" in cfg.critical_services

def test_validation_rule_update(db_session):
    updated = ValidationRuleEngine.update_config(db_session, {"max_acceptable_latency_ms": 650.0})
    assert updated.max_acceptable_latency_ms == 650.0

    # Reset back to default
    restored = ValidationRuleEngine.update_config(db_session, {"max_acceptable_latency_ms": 500.0})
    assert restored.max_acceptable_latency_ms == 500.0

def test_validation_rules_documentation():
    rules = ValidationRuleEngine.get_rules_documentation()
    assert len(rules) >= 6
    rule_names = [r["rule_name"] for r in rules]
    assert "Service Health Verification" in rule_names
    assert "Maximum Acceptable Latency" in rule_names
