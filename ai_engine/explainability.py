"""
SentinelAI - Explainability Engine
Never returns just a risk number. Always returns:
  - risk_score
  - confidence
  - reasons (human-readable)
  - evidence (metadata-backed)
  - recommended_action

Metadata only: never inspects file contents.
"""

from typing import Any, Dict, List
from datetime import datetime


class ExplainabilityEngine:
    """Produces rich, explainable risk assessments for every prediction."""

    THREAT_LEVELS = [
        (0, 20, 'Safe'),
        (21, 40, 'Low'),
        (41, 60, 'Medium'),
        (61, 80, 'High'),
        (81, 100, 'Critical')
    ]

    # Evidence -> recommended action mapping
    RECOMMENDED_ACTIONS = {
        'late_login': 'Flag for after-hours activity review; verify with manager.',
        'large_cloud_upload': 'Investigate cloud upload; verify destination and business need.',
        'usb_usage': 'Review USB device usage; confirm authorised device.',
        'unknown_device': 'Verify new device registration with IT; consider MFA enforcement.',
        'new_browser': 'Confirm browser usage; low priority review.',
        'abnormal_session': 'Review session duration anomalies; check for automated access.',
        'location_change': 'Verify login location; possible account compromise.',
        'failed_logins': 'Investigate brute-force or credential misuse.',
        'suspicious_domain': 'Analyse network connections to suspicious domains.',
        'external_email': 'Review external email recipients for data leakage.',
        'vpn_anomaly': 'Review VPN usage patterns for exfiltration.'
    }

    def __init__(self) -> None:
        self.last_explanation: Dict[str, Any] = {}

    def explain(
        self,
        risk_score: float,
        confidence: float,
        deviations: Dict[str, Any] = None,
        correlation: Dict[str, Any] = None,
        shap_values: List[Dict[str, Any]] = None,
        employee_id: str = None
    ) -> Dict[str, Any]:
        """
        Build an explainable risk assessment.

        Args:
            risk_score: Final aggregated risk score (0-100)
            confidence: Model confidence (0-1)
            deviations: BehaviourBaseline deviation dict
            correlation: RuleCorrelationEngine correlation result
            shap_values: Optional SHAP feature contributions
            employee_id: Employee identifier
        """
        threat_level = self._get_threat_level(risk_score)
        reasons = self._build_reasons(deviations, correlation, risk_score)
        evidence = self._build_evidence(deviations, correlation)
        recommended_actions = self._build_recommended_actions(reasons, deviations, threat_level)

        explanation = {
            'employee_id': employee_id,
            'risk_score': round(float(risk_score), 2),
            'threat_level': threat_level,
            'confidence': round(float(confidence), 3),
            'reasons': reasons,
            'evidence': evidence,
            'recommended_actions': recommended_actions,
            'correlation': correlation,
            'shap_values': shap_values or [],
            'timestamp': datetime.now().isoformat()
        }
        self.last_explanation = explanation
        return explanation

    def _get_threat_level(self, score: float) -> str:
        """Map a numeric score to a threat level."""
        for low, high, level in self.THREAT_LEVELS:
            if low <= score <= high:
                return level
        return 'Unknown'

    def _build_reasons(
        self,
        deviations: Dict[str, Any],
        correlation: Dict[str, Any],
        risk_score: float
    ) -> List[str]:
        """Build human-readable reasons from deviations and correlation."""
        reasons: List[str] = []

        if deviations:
            for key, val in deviations.items():
                if key in self.RECOMMENDED_ACTIONS:
                    detail = val.get('detail', '')
                    reasons.append(f"⚠️ {detail}")

        if correlation and correlation.get('correlated'):
            reasons.append(
                f"🔗 Correlated scenario: {correlation.get('scenario')} "
                f"(severity {correlation.get('severity')})"
            )

        if not reasons:
            reasons.append("✅ No significant behavioral anomalies detected.")

        # Cap at a reasonable number
        return reasons[:8]

    def _build_evidence(self, deviations: Dict[str, Any], correlation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build evidence objects (metadata-backed) for each signal."""
        evidence: List[Dict[str, Any]] = []

        if deviations:
            for key, val in deviations.items():
                evidence.append({
                    'signal': key,
                    'detail': val.get('detail', ''),
                    'severity': val.get('severity', 'medium'),
                    'confidence': val.get('score', 0.5)
                })

        if correlation and correlation.get('correlated'):
            evidence.append({
                'signal': 'correlated_scenario',
                'detail': correlation.get('scenario_description', ''),
                'severity': correlation.get('severity', 'medium'),
                'confidence': correlation.get('correlation_score', 0.5),
                'scenario': correlation.get('scenario')
            })

        return evidence

    def _build_recommended_actions(
        self,
        reasons: List[str],
        deviations: Dict[str, Any],
        threat_level: str
    ) -> List[str]:
        """Build recommended actions based on detected signals and threat level."""
        actions: List[str] = []

        if deviations:
            for key in deviations.keys():
                action = self.RECOMMENDED_ACTIONS.get(key)
                if action and action not in actions:
                    actions.append(action)

        # Add level-based escalation
        if threat_level in ('High', 'Critical'):
            actions.append('🚨 Escalate to incident response immediately.')
        if threat_level == 'Critical':
            actions.append('🔒 Consider restricting network and data access temporarily.')

        if not actions:
            actions.append('Monitor and continue baseline observation.')

        return actions[:6]
