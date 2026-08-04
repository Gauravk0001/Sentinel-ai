"""
SentinelAI - Feature Engineering Pipeline
Transforms raw per-vector activity logs into ML-ready features
Metadata-only (never accesses file contents).

Produces the required ML feature set:
  late_login_ratio, cloud_upload_size, usb_frequency, browser_downloads,
  external_email_ratio, new_device_count, vpn_usage, session_duration,
  failed_login_ratio, location_change_count
plus supporting composite indicators.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import warnings

warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Engineers features from raw per-vector event data without file-content access."""

    # The exact required ML feature set
    REQUIRED_FEATURES = [
        'late_login_ratio', 'cloud_upload_size', 'usb_frequency',
        'browser_downloads', 'external_email_ratio', 'new_device_count',
        'vpn_usage', 'session_duration', 'failed_login_ratio',
        'location_change_count'
    ]

    # Additional composite / supporting features
    SUPPORTING_FEATURES = [
        'login_frequency', 'off_hours_ratio', 'usb_transfer_volume',
        'cloud_upload_count', 'large_upload_ratio', 'email_attachment_ratio',
        'network_upload_volume', 'suspicious_domain_ratio', 'app_diversity',
        'working_hours_deviation', 'weekend_activity_ratio',
        'data_exfiltration_score', 'behavioral_anomaly_score'
    ]

    def __init__(self) -> None:
        self.feature_columns: List[str] = []

    def create_feature_matrix(self, employees: pd.DataFrame, events: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Build a complete feature matrix for all employees.

        Args:
            employees: DataFrame of employee records
            events: Dict of vector name -> events DataFrame
                    (keys: login_events, usb_events, cloud_events, network_events,
                     browser_events, email_events, application_events)
        """
        print("🔬 Engineering features from metadata...")

        login_events = events.get('login_events', pd.DataFrame())
        usb_events = events.get('usb_events', pd.DataFrame())
        cloud_events = events.get('cloud_events', pd.DataFrame())
        network_events = events.get('network_events', pd.DataFrame())
        browser_events = events.get('browser_events', pd.DataFrame())
        email_events = events.get('email_events', pd.DataFrame())
        app_events = events.get('application_events', pd.DataFrame())

        rows = []
        for _, emp in employees.iterrows():
            emp_id = emp['employee_id']
            features = self._extract_employee_features(
                emp_id,
                login_events, usb_events, cloud_events, network_events,
                browser_events, email_events, app_events
            )
            features['employee_id'] = emp_id
            features['department'] = emp['department']
            features['risk_profile'] = 1 if emp['risk_profile'] == 'malicious' else 0
            rows.append(features)

        feature_df = pd.DataFrame(rows).fillna(0)
        self.feature_columns = self.REQUIRED_FEATURES + self.SUPPORTING_FEATURES
        print(f"✅ Feature matrix created: {feature_df.shape[0]} employees x {feature_df.shape[1]} features")
        return feature_df

    def _extract_employee_features(
        self,
        emp_id: str,
        login_events: pd.DataFrame,
        usb_events: pd.DataFrame,
        cloud_events: pd.DataFrame,
        network_events: pd.DataFrame,
        browser_events: pd.DataFrame,
        email_events: pd.DataFrame,
        app_events: pd.DataFrame
    ) -> Dict[str, Any]:
        """Extract all features for a single employee from per-vector frames."""
        f: Dict[str, Any] = {}

        # --- Login-based features ---
        login = login_events[login_events['employee_id'] == emp_id] if not login_events.empty else pd.DataFrame()
        lc = len(login)
        work_start = 9
        work_end = 17

        if lc > 0:
            # late_login_ratio: fraction of logins outside working hours
            if 'hour' in login.columns:
                late = ((login['hour'] < work_start) | (login['hour'] > work_end)).sum()
                f['late_login_ratio'] = late / lc
            else:
                f['late_login_ratio'] = 0.0

            # failed_login_ratio: fraction of attempts involving failures
            if 'failed_attempts' in login.columns:
                f['failed_login_ratio'] = login['failed_attempts'].sum() / max(lc, 1)
            else:
                f['failed_login_ratio'] = 0.0

            # new_device_count: number of distinct new devices
            if 'is_new_device' in login.columns:
                f['new_device_count'] = int(login['is_new_device'].sum())
            else:
                f['new_device_count'] = 0

            # vpn_usage: fraction of logins using VPN
            if 'is_vpn_used' in login.columns:
                f['vpn_usage'] = float(login['is_vpn_used'].mean())
            else:
                f['vpn_usage'] = 0.0

            # session_duration: average session length in minutes
            if 'session_duration_minutes' in login.columns:
                f['session_duration'] = float(login['session_duration_minutes'].mean())
            else:
                f['session_duration'] = 0.0

            # location_change_count: number of distinct countries
            if 'country' in login.columns:
                f['location_change_count'] = int(login['country'].nunique())
            else:
                f['location_change_count'] = 0

            # login_frequency
            f['login_frequency'] = round(lc / 30.0, 3)
            # off_hours_ratio
            f['off_hours_ratio'] = f['late_login_ratio']
        else:
            f.update({
                'late_login_ratio': 0.0, 'failed_login_ratio': 0.0,
                'new_device_count': 0, 'vpn_usage': 0.0,
                'session_duration': 0.0, 'location_change_count': 0,
                'login_frequency': 0.0, 'off_hours_ratio': 0.0
            })

        # --- USB features ---
        usb = usb_events[usb_events['employee_id'] == emp_id] if not usb_events.empty else pd.DataFrame()
        uc = len(usb)
        f['usb_frequency'] = round(uc / 30.0, 3)
        if uc > 0 and 'transfer_size_mb' in usb.columns:
            f['usb_transfer_volume'] = float(usb['transfer_size_mb'].sum())
        else:
            f['usb_transfer_volume'] = 0.0

        # --- Cloud features ---
        cloud = cloud_events[cloud_events['employee_id'] == emp_id] if not cloud_events.empty else pd.DataFrame()
        cc = len(cloud)
        f['cloud_upload_count'] = cc
        if cc > 0 and 'upload_size_mb' in cloud.columns:
            f['cloud_upload_size'] = float(cloud['upload_size_mb'].sum())
            f['large_upload_ratio'] = float(cloud['is_large_upload'].sum() / cc) if 'is_large_upload' in cloud.columns else 0.0
        else:
            f['cloud_upload_size'] = 0.0
            f['large_upload_ratio'] = 0.0

        # --- Browser features ---
        browser = browser_events[browser_events['employee_id'] == emp_id] if not browser_events.empty else pd.DataFrame()
        if not browser.empty and 'downloads' in browser.columns:
            f['browser_downloads'] = int(browser['downloads'].sum())
        else:
            f['browser_downloads'] = 0

        # --- Email features ---
        email = email_events[email_events['employee_id'] == emp_id] if not email_events.empty else pd.DataFrame()
        ec = len(email)
        if ec > 0:
            if 'external_recipients' in email.columns:
                f['external_email_ratio'] = float((email['external_recipients'] > 3).mean())
            else:
                f['external_email_ratio'] = 0.0
            if 'has_large_attachments' in email.columns:
                f['email_attachment_ratio'] = float(email['has_large_attachments'].mean())
            else:
                f['email_attachment_ratio'] = 0.0
        else:
            f['external_email_ratio'] = 0.0
            f['email_attachment_ratio'] = 0.0

        # --- Network features ---
        network = network_events[network_events['employee_id'] == emp_id] if not network_events.empty else pd.DataFrame()
        nc = len(network)
        if nc > 0:
            if 'upload_volume_mb' in network.columns:
                f['network_upload_volume'] = float(network['upload_volume_mb'].sum())
            else:
                f['network_upload_volume'] = 0.0
            if 'is_suspicious_domain' in network.columns:
                f['suspicious_domain_ratio'] = float(network['is_suspicious_domain'].mean())
            else:
                f['suspicious_domain_ratio'] = 0.0
        else:
            f['network_upload_volume'] = 0.0
            f['suspicious_domain_ratio'] = 0.0

        # --- Application features ---
        app = app_events[app_events['employee_id'] == emp_id] if not app_events.empty else pd.DataFrame()
        if not app.empty and 'application' in app.columns:
            f['app_diversity'] = int(app['application'].nunique())
        else:
            f['app_diversity'] = 0

        # --- Temporal / composite features ---
        f['working_hours_deviation'] = self._calc_working_hours_deviation(f.get('late_login_ratio', 0.0))
        f['weekend_activity_ratio'] = 0.0
        f['data_exfiltration_score'] = self._calc_exfiltration_score(f)
        f['behavioral_anomaly_score'] = self._calc_behavioral_anomaly(f)

        return f

    def _calc_working_hours_deviation(self, late_login_ratio: float) -> float:
        """Approximate working-hours deviation from late-login ratio."""
        return min(late_login_ratio, 1.0)

    def _calc_exfiltration_score(self, f: Dict[str, Any]) -> float:
        """Composite data-exfiltration indicator from multiple metadata signals."""
        score = 0.0
        if f.get('usb_transfer_volume', 0) > 500:
            score += 0.3
        if f.get('cloud_upload_size', 0) > 200:
            score += 0.3
        if f.get('network_upload_volume', 0) > 500:
            score += 0.2
        if f.get('suspicious_domain_ratio', 0) > 0.3:
            score += 0.2
        if f.get('external_email_ratio', 0) > 0.5:
            score += 0.1
        return min(score, 1.0)

    def _calc_behavioral_anomaly(self, f: Dict[str, Any]) -> float:
        """Composite behavioral anomaly score."""
        score = 0.0
        score += f.get('late_login_ratio', 0) * 0.3
        score += min(f.get('failed_login_ratio', 0) / 3.0, 0.2)
        score += min(f.get('new_device_count', 0) * 0.05, 0.2)
        score += f.get('vpn_usage', 0) * 0.1
        score += min(f.get('location_change_count', 0) * 0.1, 0.2)
        return min(score, 1.0)

    def get_all_feature_names(self) -> List[str]:
        """Return all feature names."""
        return self.REQUIRED_FEATURES + self.SUPPORTING_FEATURES


if __name__ == '__main__':
    print("Testing Feature Engineering Pipeline...")
    fe = FeatureEngineer()
    print(f"Required features: {len(fe.REQUIRED_FEATURES)}")
    print(f"Total features: {len(fe.get_all_feature_names())}")
