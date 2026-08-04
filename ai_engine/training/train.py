"""
SentinelAI - Training Script
Trains the full AI pipeline and registers a new model version.

Usage:
    python -m ai_engine.training.train [--dataset DIR] [--events N]
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.prediction_service import create_prediction_service


def main() -> None:
    """Run the training pipeline."""
    parser = argparse.ArgumentParser(description='Train SentinelAI models')
    parser.add_argument('--dataset', type=str, default='dataset', help='Dataset directory')
    parser.add_argument('--generate', action='store_true', help='Generate dataset first if missing')
    args = parser.parse_args()

    # Ensure dataset exists
    employees_csv = os.path.join(args.dataset, 'employees.csv')
    if not os.path.exists(employees_csv) and args.generate:
        print("📦 Generating synthetic dataset...")
        from dataset.generator import SentinelDatasetGenerator
        gen = SentinelDatasetGenerator(num_employees=1000, num_events=200000)
        gen.generate_all()

    print("\n🚀 Starting SentinelAI training...")
    svc = create_prediction_service()
    svc.load_dataset(args.dataset)
    summary = svc.train()
    print("\n📊 Training summary:")
    print(f"  Model version: {summary['model_version']}")
    print(f"  Trained at: {summary['trained_at']}")
    print(f"  Metrics: {summary['metrics']}")
    print(f"  Risk distribution: {summary['risk_distribution']}")


if __name__ == '__main__':
    main()
