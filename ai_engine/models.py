"""
SentinelAI - AI Models Module
Isolation Forest + XGBoost + SHAP Explainability
Detects insider threats WITHOUT inspecting file contents
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import shap
import joblib
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """AI-Powered anomaly detection using Isolation Forest"""
    
    def __init__(self, contamination=0.05, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=200,
            max_samples='auto',
            bootstrap=False,
            n_jobs=-1,
            verbose=0
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, features: pd.DataFrame, feature_cols: List[str]):
        """Fit the isolation forest model"""
        print("🧠 Training Isolation Forest model...")
        
        X = features[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(X_scaled)
        self.is_fitted = True
        self.feature_cols = feature_cols
        
        print("✅ Isolation Forest model trained")
        return self
    
    def predict_anomaly(self, features: pd.DataFrame) -> np.ndarray:
        """Predict anomaly scores (-1 for anomaly, 1 for normal)"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
        
        X = features[self.feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        return predictions, scores
    
    def get_risk_scores(self, features: pd.DataFrame) -> np.ndarray:
        """Convert isolation forest scores to 0-100 risk scores"""
        _, scores = self.predict_anomaly(features)
        
        # Normalize scores to 0-100 range
        # Isolation Forest scores are negative for anomalies
        min_score = np.min(scores)
        max_score = np.max(scores)
        
        if max_score == min_score:
            return np.full_like(scores, 50)
        
        # Invert so higher score = higher risk
        normalized = 1 - (scores - min_score) / (max_score - min_score)
        risk_scores = normalized * 100
        
        return risk_scores


class XGBoostRiskScorer:
    """XGBoost model for refined risk scoring"""
    
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            objective='binary:logistic',
            eval_metric='auc',
            use_label_encoder=False,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, features: pd.DataFrame, target: pd.Series):
        """Train XGBoost model"""
        print("🧠 Training XGBoost model...")
        
        feature_cols = [c for c in features.columns if c not in ['employee_id', 'department', 'risk_profile']]
        self.feature_cols = feature_cols
        
        X = features[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(
            X_scaled, target,
            eval_set=[(X_scaled, target)],
            verbose=False
        )
        self.is_fitted = True
        
        # Calculate feature importance
        self.feature_importance = dict(zip(feature_cols, self.model.feature_importances_))
        
        print("✅ XGBoost model trained")
        return self
    
    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """Predict probability of being malicious"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
        
        X = features[self.feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict_proba(X_scaled)[:, 1]


class SHAPExplainer:
    """SHAP-based explainability for risk scores"""
    
    def __init__(self):
        self.explainer = None
        self.is_fitted = False
        
    def fit(self, model, features: pd.DataFrame):
        """Initialize SHAP explainer"""
        print("🔍 Setting up SHAP explainer...")
        
        feature_cols = [c for c in features.columns if c not in ['employee_id', 'department', 'risk_profile']]
        self.feature_cols = feature_cols
        self.feature_names = feature_cols
        
        # Use TreeExplainer for XGBoost
        self.explainer = shap.TreeExplainer(model.model)
        self.is_fitted = True
        
        print("✅ SHAP explainer ready")
        return self
    
    def explain_risk(self, features: pd.DataFrame, employee_id: str) -> Dict:
        """
        Generate SHAP-based explanation for why an employee is risky
        WITHOUT referencing file contents
        """
        if not self.is_fitted:
            return self._rule_based_explanation(features)
        
        emp_features = features[features['employee_id'] == employee_id]
        
        if len(emp_features) == 0:
            return self._rule_based_explanation(features)
        
        X = emp_features[self.feature_cols].values
        
        try:
            shap_values = self.explainer.shap_values(X)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            # Get top contributing features
            feature_impacts = []
            for i, col in enumerate(self.feature_cols):
                impact = float(shap_values[0, i]) if len(shap_values.shape) > 1 else float(shap_values[i])
                feature_impacts.append({
                    'feature': col,
                    'impact': impact,
                    'value': float(X[0, i])
                })
            
            # Sort by absolute impact
            feature_impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            # Generate human-readable reasons
            reasons = self._generate_reasons(feature_impacts[:5])
            
            return {
                'shap_values': feature_impacts[:10],
                'reasons': reasons,
                'type': 'shap'
            }
            
        except Exception as e:
            print(f"SHAP error: {e}, falling back to rule-based")
            return self._rule_based_explanation(features, employee_id)
    
    def _rule_based_explanation(self, features: pd.DataFrame, employee_id: Optional[str] = None) -> Dict:
        """Fallback: Rule-based explanation when SHAP is unavailable"""
        reasons = []
        
        if employee_id:
            emp_features = features[features['employee_id'] == employee_id]
        else:
            emp_features = features
        
        if len(emp_features) == 0:
            return {'reasons': ['No activity data available'], 'type': 'rule_based', 'shap_values': []}
        
        row = emp_features.iloc[0]
        
        # Check various risk indicators
        if row.get('off_hours_ratio', 0) > 0.4:
            reasons.append('⚠️ Abnormal working hours - Multiple logins outside business hours')
        
        if row.get('failed_login_ratio', 0) > 0.3:
            reasons.append('🔐 High failed login attempts - Possible brute force or credential misuse')
        
        if row.get('new_device_ratio', 0) > 0.3:
            reasons.append('💻 Multiple new devices detected - Unusual device switching pattern')
        
        if row.get('sensitive_file_access_ratio', 0) > 0.4:
            reasons.append('📁 Excessive access to sensitive directories')
        
        if row.get('usb_events', 0) > 3:
            reasons.append(f'🔌 Unusual USB activity - {int(row["usb_events"])} USB events detected')
        
        if row.get('usb_transfer_volume', 0) > 500:
            reasons.append(f'💾 Large USB data transfer - {row["usb_transfer_volume"]:.0f}MB transferred to USB')
        
        if row.get('cloud_upload_count', 0) > 5:
            reasons.append(f'☁️ Multiple cloud uploads - {int(row["cloud_upload_count"])} upload events to cloud services')
        
        if row.get('cloud_upload_volume', 0) > 200:
            reasons.append(f'📤 Large cloud data exfiltration - {row["cloud_upload_volume"]:.0f}MB uploaded to cloud')
        
        if row.get('download_count', 0) > 50:
            reasons.append(f'⬇️ Bulk file download detected - {int(row["download_count"])} files downloaded')
        
        if row.get('external_email_ratio', 0) > 0.5:
            reasons.append('📧 High ratio of emails to external recipients')
        
        if row.get('email_attachment_ratio', 0) > 0.5:
            reasons.append('📎 Multiple emails with large attachments')
        
        if row.get('suspicious_domain_ratio', 0) > 0.3:
            reasons.append('🌐 Connections to suspicious domains detected (pastebin, mega.nz, etc.)')
        
        if row.get('network_upload_volume', 0) > 500:
            reasons.append(f'📶 High network upload volume - {row["network_upload_volume"]:.0f}MB uploaded')
        
        if row.get('working_hours_deviation', 0) > 0.5:
            reasons.append('⏰ Significant deviation from normal working hours pattern')
        
        if row.get('weekend_activity_ratio', 0) > 0.4:
            reasons.append('📅 High weekend activity - Unusual for this employee\'s pattern')
        
        if row.get('app_diversity', 10) < 3:
            reasons.append('🖥️ Unusually low application diversity - Possible automated data gathering')
        
        if not reasons:
            reasons.append('✅ No significant behavioral anomalies detected')
        
        return {
            'reasons': reasons[:8],  # Max 8 reasons
            'type': 'rule_based',
            'shap_values': []
        }
    
    def _generate_reasons(self, top_features: List[Dict]) -> List[str]:
        """Convert SHAP values to human-readable reasons"""
        reason_map = {
            'off_hours_ratio': lambda v: f'⚠️ {v["impact"]*100:.0f}% risk contribution from abnormal working hours',
            'failed_login_ratio': lambda v: f'🔐 {v["impact"]*100:.0f}% risk from failed login attempts',
            'new_device_ratio': lambda v: f'💻 {v["impact"]*100:.0f}% risk from new device usage',
            'sensitive_file_access_ratio': lambda v: f'📁 {v["impact"]*100:.0f}% risk from sensitive directory access',
            'usb_events': lambda v: f'🔌 {v["impact"]*100:.0f}% risk from USB device events',
            'usb_transfer_volume': lambda v: f'💾 {v["impact"]*100:.0f}% risk from USB data transfer volume',
            'cloud_upload_count': lambda v: f'☁️ {v["impact"]*100:.0f}% risk from cloud upload frequency',
            'cloud_upload_volume': lambda v: f'📤 {v["impact"]*100:.0f}% risk from cloud upload volume',
            'download_count': lambda v: f'⬇️ {v["impact"]*100:.0f}% risk from bulk downloads',
            'external_email_ratio': lambda v: f'📧 {v["impact"]*100:.0f}% risk from external email communications',
            'suspicious_domain_ratio': lambda v: f'🌐 {v["impact"]*100:.0f}% risk from suspicious domain connections',
            'network_upload_volume': lambda v: f'📶 {v["impact"]*100:.0f}% risk from network upload volume',
            'data_exfiltration_score': lambda v: f'🚨 {v["impact"]*100:.0f}% risk from combined exfiltration signals',
            'behavioral_anomaly_score': lambda v: f'🔄 {v["impact"]*100:.0f}% risk from behavioral anomalies',
        }
        
        reasons = []
        for feat in top_features[:6]:
            feature_name = feat['feature']
            if feature_name in reason_map:
                try:
                    reason = reason_map[feature_name](feat)
                    reasons.append(reason)
                except:
                    reasons.append(f'Risk contribution from {feature_name.replace("_", " ")}')
        
        return reasons


class RiskEngine:
    """Combined AI Risk Engine - Scores + Explainability"""
    
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.risk_scorer = XGBoostRiskScorer()
        self.explainer = SHAPExplainer()
        self.threat_levels = {
            (0, 20): 'Safe',
            (21, 40): 'Low',
            (41, 60): 'Medium',
            (61, 80): 'High',
            (81, 100): 'Critical'
        }
        
    def train(self, features: pd.DataFrame):
        """Train all AI models"""
        print("\n🚀 Training SentinelAI AI Engine...")
        
        # Prepare features
        feature_cols = [c for c in features.columns if c not in ['employee_id', 'department', 'risk_profile']]
        
        # Train Isolation Forest
        self.anomaly_detector.fit(features, feature_cols)
        
        # Train XGBoost
        target = features['risk_profile']
        self.risk_scorer.fit(features, target)
        
        # Setup SHAP
        self.explainer.fit(self.risk_scorer, features)
        
        print("✅ AI Engine training complete!\n")
        return self
    
    def evaluate_employee(self, features: pd.DataFrame, employee_id: str) -> Dict:
        """
        Evaluate a single employee and return comprehensive risk assessment
        WITHOUT inspecting file contents
        """
        emp_features = features[features['employee_id'] == employee_id]
        
        if len(emp_features) == 0:
            return {
                'employee_id': employee_id,
                'error': 'Employee not found'
            }
        
        # Get Isolation Forest risk score
        if_score = self.anomaly_detector.get_risk_scores(emp_features)[0]
        
        # Get XGBoost probability
        if self.risk_scorer.is_fitted:
            xgb_score = self.risk_scorer.predict_proba(emp_features)[0] * 100
        else:
            xgb_score = if_score
        
        # Combined score (weighted average)
        combined_score = (if_score * 0.4 + xgb_score * 0.6)
        
        # Get threat level
        threat_level = self._get_threat_level(combined_score)
        
        # Get explanation
        explanation = self.explainer.explain_risk(features, employee_id)
        
        # Determine confidence
        confidence = self._calculate_confidence(combined_score, explanation)
        
        # Suggested actions
        suggested_actions = self._get_suggested_actions(threat_level, explanation)
        
        return {
            'employee_id': employee_id,
            'risk_score': round(float(combined_score), 2),
            'isolation_forest_score': round(float(if_score), 2),
            'xgboost_score': round(float(xgb_score), 2),
            'threat_level': threat_level,
            'confidence': confidence,
            'reasons': explanation.get('reasons', []),
            'shap_values': explanation.get('shap_values', []),
            'suggested_actions': suggested_actions,
            'timestamp': datetime.now().isoformat(),
            'model_version': 'SentinelAI v1.0'
        }
    
    def evaluate_all(self, features: pd.DataFrame) -> pd.DataFrame:
        """Evaluate all employees and return risk assessments"""
        print("📊 Evaluating all employees...")
        
        results = []
        for emp_id in features['employee_id'].unique():
            result = self.evaluate_employee(features, emp_id)
            results.append(result)
        
        result_df = pd.DataFrame(results)
        print(f"✅ Evaluated {len(results)} employees")
        return result_df
    
    def _get_threat_level(self, score: float) -> str:
        """Convert numeric score to threat level"""
        for (low, high), level in self.threat_levels.items():
            if low <= score <= high:
                return level
        return 'Unknown'
    
    def _calculate_confidence(self, score: float, explanation: Dict) -> float:
        """Calculate confidence in the prediction"""
        base_confidence = 0.7
        
        # Higher confidence for extreme scores
        if score > 80 or score < 10:
            base_confidence += 0.15
        
        # Higher confidence with more reasons
        num_reasons = len(explanation.get('reasons', []))
        base_confidence += min(num_reasons * 0.02, 0.1)
        
        # SHAP explanations boost confidence
        if explanation.get('type') == 'shap':
            base_confidence += 0.1
        
        return round(min(base_confidence, 0.99), 2)
    
    def _get_suggested_actions(self, threat_level: str, explanation: Dict) -> List[str]:
        """Get suggested actions based on threat level"""
        actions = {
            'Safe': ['No action required'],
            'Low': ['Monitor employee activity', 'Send awareness reminder'],
            'Medium': [
                'Review recent activity logs',
                'Flag employee for observation',
                'Notify team lead'
            ],
            'High': [
                'Immediate review of recent activities',
                'Restrict sensitive data access',
                'Schedule security interview',
                'Enable enhanced monitoring'
            ],
            'Critical': [
                '🚨 IMMEDIATE ACTION REQUIRED',
                'Disable network access temporarily',
                'Block USB ports remotely',
                'Revoke cloud access permissions',
                'Initiate incident response protocol',
                'Preserve all logs for investigation',
                'Contact employee\'s manager immediately'
            ]
        }
        
        return actions.get(threat_level, ['Review activity'])
    
    def save_models(self, path: str = 'models/'):
        """Save trained models to disk"""
        import os
        os.makedirs(path, exist_ok=True)
        
        joblib.dump(self.anomaly_detector.model, f'{path}/isolation_forest.pkl')
        joblib.dump(self.risk_scorer.model, f'{path}/xgboost_model.pkl')
        joblib.dump(self.anomaly_detector.scaler, f'{path}/scaler.pkl')
        
        # Save config
        config = {
            'contamination': self.anomaly_detector.contamination,
            'feature_cols': self.anomaly_detector.feature_cols,
            'trained_at': datetime.now().isoformat()
        }
        with open(f'{path}/model_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Models saved to {path}")
    
    def load_models(self, path: str = 'models/'):
        """Load trained models from disk"""
        import os
        if not os.path.exists(path):
            raise FileNotFoundError(f"Models not found at {path}")
        
        self.anomaly_detector.model = joblib.load(f'{path}/isolation_forest.pkl')
        self.risk_scorer.model = joblib.load(f'{path}/xgboost_model.pkl')
        self.anomaly_detector.scaler = joblib.load(f'{path}/scaler.pkl')
        self.anomaly_detector.is_fitted = True
        self.risk_scorer.is_fitted = True
        
        print(f"📂 Models loaded from {path}")
        return self


if __name__ == '__main__':
    print("Testing AI Models...")
    engine = RiskEngine()
    print("✅ Models loaded successfully")

