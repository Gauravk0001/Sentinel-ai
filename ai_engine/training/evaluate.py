"""
SentinelAI - Evaluation Script
Evaluates the trained model against the dataset and reports metrics.

Usage:
    python -m ai_engine.training.evaluate [--dataset DIR]
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.prediction_service import create_prediction_service


def main() -> None:
    """Evaluate the model."""
    parser = argparse.ArgumentParser(description='Evaluate SentinelAI model')
    parser.add_argument('--dataset', type=str, default='dataset', help='Dataset directory')
    args = parser.parse_args()

    svc = create_prediction_service()
    svc.load_dataset(args.dataset)
    if svc.features is None:
        svc.train()

    print("\n📈 Evaluating model performance...")

    # Predict all
    results = svc.predict_all()
    result_df = pd.DataFrame(results)

    # Actual labels from features
    actual = svc.features['risk_profile'].values

    # Predicted risk (anomaly > 60)
    pred = (result_df['risk_score'].values > 60).astype(int)

    # Metrics
    n = len(actual)
    tp = int(((pred == 1) & (actual == 1)).sum())
    fp = int(((pred == 1) & (actual == 0)).sum())
    tn = int(((pred == 0) & (actual == 0)).sum())
    fn = int(((pred == 0) & (actual == 1)).sum())

    accuracy = (tp + tn) / max(n, 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)

    print(f"\n  Total employees: {n}")
    print(f"  True positives: {tp}")
    print(f"  False positives: {fp}")
    print(f"  True negatives: {tn}")
    print(f"  False negatives: {fn}")
    print(f"\n  Accuracy : {accuracy:.3f}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall   : {recall:.3f}")
    print(f"  F1-score : {f1:.3f}")

    # Risk distribution
    print("\n  Risk distribution:")
    dist = svc._risk_distribution()
    for level, count in dist.items():
        print(f"    {level.capitalize():>10}: {count}")

    # Save metrics to active model entry
    active = svc.registry.get_active_model()
    if active:
        active['metrics']['evaluation'] = {
            'accuracy': round(accuracy, 3),
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1': round(f1, 3)
        }
        svc.registry._save_registry()
        print(f"\n  ✅ Metrics saved to model {active['model_version']}")


if __name__ == '__main__':
    main()
