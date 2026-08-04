"""
SentinelAI - Behaviour Baseline Engine
Builds a per-employee behavioural baseline from historical metadata
and scores new behaviour against that baseline.

Metadata-only: never inspects file contents.
"""

from typing import Any, Dict, List
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


class BehaviourBaseline:
    """
    Computes and stores a normal-behaviour baseline per employee.

    Baseline dimensions:
      - normal_login_hour
      - normal_upload_size (MB)
      - normal_usb_frequency
      - normal_device_id
      - normal_browser
      - normal_session_duration (minutes)
      - normal_location
    """

    BASELINE_FIELDS = [
        'normal_login_hour', 'normal_upload_size', 'normal_usb_frequency',
        'normal_device', 'normal_browser', 'normal_session_duration',
        'normal_location'
    ]

    def __init__(self) -> None:
        # employee_id -> baseline dict
        self.baselines: Dict[str, Dict[str, Any]] = {}
        self._employee_count: int = 0
        self._event_frames: Dict[str, pd.DataFrame] = {}
        self.num_days: int = 60

    def fit(self, employees: pd.DataFrame, events: Dict[str, pd.DataFrame]) -> None:
        """
        Build baselines from historical event data.

        Args:
            employees: DataFrame with employee records (employee_id etc.)
            events: Dict of vector name -> events DataFrame
        """
        print("🧬 Building behaviour baselines...")

        emp_map = {}
        for _, emp in employees.iterrows():
            emp_map[emp['employee_id']] = emp

        login_events = events.get('login_events', pd.DataFrame())
        usb_events = events.get('usb_events', pd.DataFrame())
        cloud_events = events.get('cloud_events', pd.DataFrame())
        network_events = events.get('network_events', pd.DataFrame())
        browser_events = events.get('browser_events', pd.DataFrame())

        for emp_id, emp in emp_map.items():
            baseline: Dict[str, Any] = {
                'employee_id': emp_id,
                'department': emp.get('department', 'Unknown'),
                'normal_login_hour': float(emp.get('working_hours_start', 9)),
                'normal_upload_size': 10.0,
                'normal_usb_frequency': 1.0,
                'normal_device': str(emp.get('device_id', 'unknown')),
                'normal_browser': 'Chrome',
                'normal_session_duration': 120.0,
                'normal_location': str(emp.get('location', 'Unknown')),
                'login_hour_std': 2.0,
                'upload_size_std': 8.0,
                'session_duration_std': 40.0,
                '_event_counts': 0
            }

            # --- Login baseline ---
            if not login_events.empty:
                login = login_events[login_events['employee_id'] == emp_id]
                if len(login) > 0:
                    if 'hour' in login.columns:
                        baseline['normal_login_hour'] = float(login['hour'].mean())
                        baseline['login_hour_std'] = max(float(login['hour'].std()), 0.5)
                    if 'session_duration_minutes' in login.columns:
                        baseline['normal_session_duration'] = float(login['session_duration_minutes'].mean())
                        baseline['session_duration_std'] = max(float(login['session_duration_minutes'].std()), 10.0)
                    if 'is_new_device' in login.columns:
                        known = login[login['is_new_device'] == False]  # noqa: E712
                        if len(known) > 0 and 'device_id' in known.columns:
                            baseline['normal_device'] = str(known['device_id'].mode().iloc[0])
                    if 'browser' in login.columns:
                        baseline['normal_browser'] = str(login['browser'].mode().iloc[0])
                    if 'country' in login.columns:
                        baseline['normal_location'] = str(login['country'].mode().iloc[0])

            # --- USB frequency baseline ---
            if not usb_events.empty:
                usb = usb_events[usb_events['employee_id'] == emp_id]
                baseline['normal_usb_frequency'] = float(len(usb) / max(self.num_days, 1))

            # --- Cloud upload size baseline ---
            if not cloud_events.empty:
                cloud = cloud_events[cloud_events['employee_id'] == emp_id]
                if len(cloud) > 0 and 'upload_size_mb' in cloud.columns:
                    baseline['normal_upload_size'] = float(cloud['upload_size_mb'].mean())
                    baseline['upload_size_std'] = max(float(cloud['upload_size_mb'].std()), 5.0)

            # --- Network upload baseline ---
            if not network_events.empty and 'upload_volume_mb' in network_events.columns:
                net = network_events[network_events['employee_id'] == emp_id]
                if len(net) > 0:
                    baseline['network_upload_baseline'] = float(net['upload_volume_mb'].mean())

            baseline['_event_counts'] = int(len(login_events[login_events['employee_id'] == emp_id]))
            self.baselines[emp_id] = baseline

        self._employee_count = len(emp_map)
        print(f"✅ Baselines built for {self._employee_count} employees")
        return self

    def get_baseline(self, employee_id: str) -> Dict[str, Any]:
        """Get the baseline for a specific employee."""
        return self.baselines.get(employee_id, {})

    def score_deviation(self, employee_id: str, current: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current behaviour to baseline and return per-dimension deviations.

        Args:
            employee_id: Employee identifier
            current: Dict of current behaviour values, e.g.
                     {'login_hour': 2, 'upload_size': 800, 'usb_frequency': 5,
                      'device_id': '...', 'browser': 'Tor', 'session_duration': 30,
                      'location': 'Russia'}
        """
        baseline = self.get_baseline(employee_id)
        if not baseline:
            return {'deviations': {}, 'anomaly_count': 0, 'total_anomaly_score': 0.0}

        deviation_score = 0.0
        deviations: Dict[str, Any] = {}

        # --- Login hour deviation ---
        if 'login_hour' in current:
            base_hour = baseline.get('normal_login_hour', 9)
            std = baseline.get('login_hour_std', 2.0) or 2.0
            diff = abs(float(current['login_hour']) - float(base_hour))
            z = diff / std
            if z > 1.5:
                score = min(z / 4.0, 1.0)
                deviations['late_login'] = {
                    'score': score,
                    'detail': f'Login at hour {current["login_hour"]:.0f} vs baseline {base_hour:.0f}',
                    'severity': 'high' if score > 0.6 else 'medium'
                }
                deviation_score += score

        # --- Upload size deviation ---
        if 'upload_size' in current:
            base_upload = baseline.get('normal_upload_size', 10.0) or 10.0
            ratio = float(current['upload_size']) / max(float(base_upload), 0.1)
            if ratio > 3.0:
                score = min(ratio / 10.0, 1.0)
                deviations['large_cloud_upload'] = {
                    'score': score,
                    'detail': f'Upload {current["upload_size"]:.0f}MB vs baseline {base_upload:.0f}MB',
                    'severity': 'high' if score > 0.6 else 'medium'
                }
                deviation_score += score

        # --- USB frequency deviation ---
        if 'usb_frequency' in current:
            base_usb = baseline.get('normal_usb_frequency', 1.0) or 1.0
            ratio = float(current['usb_frequency']) / max(float(base_usb), 0.1)
            if ratio > 3.0:
                score = min(ratio / 6.0, 1.0)
                deviations['usb_usage'] = {
                    'score': score,
                    'detail': f'USB frequency {current["usb_frequency"]:.1f} vs baseline {base_usb:.1f}',
                    'severity': 'high' if score > 0.6 else 'medium'
                }
                deviation_score += score

        # --- Device deviation ---
        if 'device_id' in current:
            base_device = baseline.get('normal_device', 'unknown')
            if str(current['device_id']) != str(base_device):
                deviations['unknown_device'] = {
                    'score': 0.8,
                    'detail': f'Login from unknown device {current["device_id"]}',
                    'severity': 'high'
                }
                deviation_score += 0.6

        # --- Browser deviation ---
        if 'browser' in current:
            base_browser = baseline.get('normal_browser', 'Chrome')
            if str(current['browser']) != str(base_browser):
                deviations['new_browser'] = {
                    'score': 0.35,
                    'detail': f'Browser {current["browser"]} differs from baseline {base_browser}',
                    'severity': 'medium'
                }
                deviation_score += 0.25

        # --- Session duration deviation ---
        if 'session_duration' in current:
            base_dur = baseline.get('normal_session_duration', 120.0) or 120.0
            base_std = baseline.get('session_duration_std', 40.0) or 40.0
            diff = abs(float(current['session_duration']) - float(base_dur))
            z = diff / max(base_std, 1.0)
            if z > 1.5:
                score = min(z / 4.0, 0.7)
                deviations['abnormal_session'] = {
                    'score': score,
                    'detail': f'Session {current["session_duration"]:.0f}min vs baseline {base_dur:.0f}min',
                    'severity': 'medium'
                }
                deviation_score += score * 0.5

        # --- Location deviation ---
        if 'location' in current:
            base_loc = baseline.get('normal_location', 'Unknown')
            if str(current['location']) != str(base_loc):
                deviations['location_change'] = {
                    'score': 0.75,
                    'detail': f'Login from {current["location"]} instead of {base_loc}',
                    'severity': 'high'
                }
                deviation_score += 0.55

        total = min(deviation_score, 1.0)
        return {
            'deviations': deviations,
            'anomaly_count': len(deviations),
            'total_anomaly_score': round(total, 3)
        }

    def build_recent_features(self, employee_id: str, window_days: int = 7) -> Dict[str, Any]:
        """
        Aggregate recent events into per-vector 'current behaviour' dict
        used by score_deviation. Metadata only.
        """
        features: Dict[str, Any] = {}

        recent = self._recent_events(employee_id, window_days)

        login = recent.get('login_events', pd.DataFrame())
        if not login.empty:
            if 'hour' in login.columns:
                features['login_hour'] = float(login['hour'].mean())
            if 'device_id' in login.columns:
                features['device_id'] = str(login['device_id'].iloc[-1])
            if 'browser' in login.columns:
                features['browser'] = str(login['browser'].iloc[-1])
            if 'session_duration_minutes' in login.columns:
                features['session_duration'] = float(login['session_duration_minutes'].mean())
            if 'country' in login.columns:
                features['location'] = str(login['country'].iloc[-1])

        cloud = recent.get('cloud_events', pd.DataFrame())
        if not cloud.empty and 'upload_size_mb' in cloud.columns:
            features['upload_size'] = float(cloud['upload_size_mb'].sum())

        usb = recent.get('usb_events', pd.DataFrame())
        if not usb.empty:
            features['usb_frequency'] = float(len(usb))

        return features

    def _recent_events(self, employee_id: str, window_days: int) -> Dict[str, pd.DataFrame]:
        """Pull recent events for an employee from stored event frames."""
        out = {}
        cutoff = datetime.now() - timedelta(days=window_days)
        for name, frame in self._event_frames.items():
            if frame.empty:
                out[name] = pd.DataFrame()
                continue
            sub = frame[frame['employee_id'] == employee_id]
            if 'timestamp' in sub.columns:
                try:
                    ts = pd.to_datetime(sub['timestamp'])
                    sub = sub[ts >= cutoff]
                except Exception:
                    pass
            out[name] = sub
        return out

    def attach_events(self, event_frames: Dict[str, pd.DataFrame], num_days: int = 60) -> None:
        """Attach raw event frames for real-time deviation scoring."""
        self._event_frames = event_frames
        self.num_days = num_days

    def get_all_baselines(self) -> List[Dict[str, Any]]:
        """Return all employee baselines."""
        return [self.baselines[eid] for eid in sorted(self.baselines.keys())]
