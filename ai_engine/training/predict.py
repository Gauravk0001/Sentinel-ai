"""
SentinelAI - Prediction Script
Runs live predictions for all or specific employees using the trained pipeline.

Usage:
    python -m ai_engine.training.predict [--employee EMP00001] [--dataset DIR]
"""

import argparse
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.prediction_service import create_prediction_service


def main() -> None:
    """Run predictions."""
    parser = argparse.ArgumentParser(description='Predict insider threat risk')
    parser.add_argument('--employee', type=str, default=None, help='Employee ID (default: all)')
    parser.add_argument('--dataset', type=str, default='dataset', help='Dataset directory')
    parser.add_argument('--json', dest='as_json', action='store_true', help='Output JSON')
    args = parser.parse_args()

    svc = create_prediction_service()
    svc.load_dataset(args.dataset)
    # Ensure model is loaded/trained
    if svc.features is None:
        svc.train()

    if args.employee:
        result = svc.predict_employee(args.employee)
        if args.as_json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\n🔍 Employee: {args.employee}")
            print(f"   Risk: {result['risk_score']}/100 ({result['threat_level']})")
            print(f"   Confidence: {result['confidence']:.0%}")
            print("   Reasons:")
            for r in result['reasons']:
                print(f"     • {r}")
            print("   Recommended actions:")
            for a in result['recommended_actions']:
                print(f"     • {a}")
    else:
        results = svc.predict_all()
        if args.as_json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"\n📊 Predicted {len(results)} employees")
            high = [r for r in results if r['risk_score'] > 60]
            print(f"   High risk: {len(high)}")
            for r in sorted(high, key=lambda x: x['risk_score'], reverse=True)[:5]:
                print(f"     {r['employee_id']}: {r['risk_score']:.0f} ({r['threat_level']})")


if __name__ == '__main__':
    main()
