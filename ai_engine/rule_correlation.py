"""
SentinelAI - Rule Correlation Engine
Correlates isolated behavioural events into coherent insider-threat scenarios.

Instead of treating single events in isolation, this engine combines
correlated signals (e.g. USB + Night Login + Cloud Upload + Unknown Device)
into a single correlated incident with an escalating severity.

Metadata only: never inspects file contents.
"""

from typing import Any, Dict, List
from datetime import datetime


class RuleCorrelationEngine:
    """
    Correlates per-vector event signals into composite threat scenarios.

    Signals are weighted; combinations of multiple high-weight signals
    produce a 'correlated_anomaly' with scenario title + severity.
    """

    # Signal weights for correlation scenarios
    SIGNAL_WEIGHTS = {
        'unknown_device': 25,
        'late_login': 20,
        'large_cloud_upload': 25,
        'usb_usage': 20,
        'location_change': 15,
        'new_browser': 5,
        'abnormal_session': 10,
        'failed_logins': 15,
        'suspicious_domain': 20,
        'external_email': 10,
        'vpn_anomaly': 15
    }

    SCENARIOS = [
        {
            'name': 'Data Exfiltration via USB + Cloud',
            'required': ['usb_usage', 'large_cloud_upload'],
            'boost': 30,
            'description': 'USB device usage combined with large cloud uploads indicates possible data exfiltration.'
        },
        {
            'name': 'Off-Hours Exfiltration Attempt',
            'required': ['late_login', 'large_cloud_upload'],
            'boost': 25,
            'description': 'Large cloud uploads occurring outside normal working hours.'
        },
        {
            'name': 'Account Compromise / Credential Misuse',
            'required': ['location_change', 'unknown_device', 'failed_logins'],
            'boost': 35,
            'description': 'Login from a new location and device with failed attempts suggests possible account compromise.'
        },
        {
            'name': 'Unauthorized Device Access',
            'required': ['unknown_device', 'late_login'],
            'boost': 20,
            'description': 'Access from an unknown device during off-hours.'
        }
    ]

    def __init__(self) -> None:
        self.last_correlation_at: str = ''

    def correlate(self, deviations: Dict[str, Any], employee_id: str) -> Dict[str, Any]:
        """
        Run correlation logic on detected deviations.

        Args:
            deviations: Output of BehaviourBaseline.score_deviation()['deviations']
            employee_id: Employee identifier

        Returns:
            Correlated anomaly result or None-scentinel if no correlation fires.
        """
        if not deviations:
            return {
                'correlated': False,
                'scenario': None,
                'correlation_score': 0.0,
                'signals': [],
                'employee_id': employee_id
            }

        present = set(deviations.keys())
        total_weight = sum(self.SIGNAL_WEIGHTS.get(sig, 0) for sig in present)
        matched_scenario = None
        best_boost = 0

        for scenario in self.SCENARIOS:
            required = set(scenario['required'])
            if required.issubset(present):
                if scenario['boost'] > best_boost:
                    best_boost = scenario['boost']
                    matched_scenario = scenario

        correlation_score = min(total_weight / 100.0, 1.0)
        if matched_scenario and correlation_score < 0.5:
            correlation_score = min(correlation_score + matched_scenario['boost'] / 100.0, 1.0)

        correlated = matched_scenario is not None

        self.last_correlation_at = datetime.now().isoformat()

        return {
            'correlated': correlated,
            'scenario': matched_scenario['name'] if matched_scenario else None,
            'scenario_description': matched_scenario['description'] if matched_scenario else None,
            'correlation_score': round(correlation_score, 3),
            'signal_count': len(present),
            'signals': list(present),
            'severity': self._severity_from_score(correlation_score, matched_scenario),
            'employee_id': employee_id,
            'timestamp': self.last_correlation_at
        }

    def _severity_from_score(self, score: float, scenario: Any) -> str:
        """Map correlation score to severity."""
        if scenario and score >= 0.7:
            return 'critical'
        if score >= 0.6:
            return 'high'
        if score >= 0.4:
            return 'medium'
        return 'low'

    def get_scenario_weights(self) -> Dict[str, int]:
        """Expose signal weights for transparency."""
        return self.SIGNAL_WEIGHTS

