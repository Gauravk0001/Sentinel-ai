"""
SentinelAI - Model Save Script
Saves the trained model artifacts to disk and registers version metadata.

Usage:
    python -m ai_engine.training.save_model [--output DIR] [--version v1.0.0]
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.prediction_service import create_prediction_service


def main() -> None:
    """Save trained models."""
    parser = argparse.ArgumentParser(description='Save SentinelAI models')
    parser.add_argument('--output', type=str, default='output/models', help='Output directory')
    parser.add_argument('--version', type=str, default=None, help='Model version (default: auto)')
    args = parser.parse_args()

    svc = create_prediction_service()
    svc.load_dataset('dataset')
    if svc.features is None:
        svc.train()

    # Save the risk engine artifacts
    svc.risk_engine.save_models(args.output)

    # Version
    if args.version:
        version = args.version
    else:
        version = f"v1.{len(svc.registry.get_all_versions()) + 1}"

    # Register in registry
    entry = svc.registry.register_model(
        version=version,
        model_path=args.output,
        metrics=svc._compute_metrics(),
        features=svc.feature_engineer.get_all_feature_names()
    )

    print(f"\n💾 Model saved to {args.output}")
    print(f"   Version: {version}")
    print(f"   Registered at: {entry['training_date']}")


if __name__ == '__main__':
    main()
