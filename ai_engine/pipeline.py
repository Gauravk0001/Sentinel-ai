"""
SentinelAI - Complete AI Pipeline
End-to-end: Data → Features → Baseline → Model → Risk Score → Explanation
Metadata-only (never inspects file contents).
"""

import os
import sys
from datetime import datetime
import json

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.prediction_service import create_prediction_service


class SentinelAIPipeline:
    """Complete AI Pipeline for Insider Threat Detection."""

    def __init__(self) -> None:
        self.service = create_prediction_service()
        self.results = None
        self.summary = {}

    def run_pipeline(self, dataset_dir: str = 'dataset') -> tuple:
        """Run the complete AI pipeline."""
        print("\n" + "=" * 60)
        print("  🤖 SENTINELAI - AI PIPELINE")
        print("=" * 60 + "\n")

        # Step 1: Load data
        print("📥 Step 1: Loading data...")
        self.service.load_dataset(dataset_dir)

        # Step 2: Train (baseline + features + models)
        print("\n🧠 Step 2: Training AI models...")
        self.summary = self.service.train()

        # Step 3: Predict all
        print("\n📊 Step 3: Predicting employee risk...")
        self.results = self.service.predict_all()

        # Step 4: Save results
        print("\n💾 Step 4: Saving results...")
        self.save_results()

        return self.results, self.summary

    def save_results(self, output_dir: str = 'output/') -> None:
        """Save pipeline results."""
        os.makedirs(output_dir, exist_ok=True)

        if self.results is not None:
            pd.DataFrame(self.results).to_csv(f'{output_dir}/risk_assessments.csv', index=False)

        if self.service.features is not None:
            self.service.features.to_csv(f'{output_dir}/feature_matrix.csv', index=False)

        # Save summary
        with open(f'{output_dir}/pipeline_summary.json', 'w') as f:
            json.dump(self.summary, f, indent=2, default=str)

        print(f"💾 Results saved to {output_dir}")

    def get_employee_details(self, employee_id: str) -> dict:
        """Get detailed risk assessment for a specific employee."""
        return self.service.predict_employee(employee_id)

    def get_high_risk_employees(self, threshold: float = 60.0) -> list:
        """Get all employees above risk threshold."""
        if self.results is None:
            return []
        return [r for r in self.results if r['risk_score'] > threshold]


def main():
    """Main entry point."""
    pipeline = SentinelAIPipeline()

    # Check if dataset exists
    if not os.path.exists('dataset/employees.csv'):
        print("📦 Generating synthetic dataset first...")
        from dataset.generator import SentinelDatasetGenerator
        generator = SentinelDatasetGenerator(num_employees=1000, num_events=200000)
        generator.generate_all()

    results, summary = pipeline.run_pipeline()

    # Show top 5 risky employees
    if results:
        print("\n🔴 TOP 5 HIGHEST RISK EMPLOYEES:")
        print("-" * 80)
        high_risk = sorted(results, key=lambda x: x['risk_score'], reverse=True)[:5]
        for i, emp in enumerate(high_risk, 1):
            print(f"  {i}. {emp['employee_id']} - Risk: {emp['risk_score']:.1f}/100 ({emp['threat_level']})")
            print(f"     Confidence: {emp['confidence']:.0%}")
            for reason in emp['reasons'][:3]:
                print(f"     • {reason}")
            print()

    print("✅ Pipeline complete!")


if __name__ == '__main__':
    main()
