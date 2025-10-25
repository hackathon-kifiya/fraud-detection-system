"""
Script to visualize SHAP explanations for sample predictions
"""
import asyncio
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import (CityOptions, EducationalLevelOptions, Gender,  # noqa: E402
                                KYCData, MaritalStatusOptions, RegionOptions,
                                TransactionData, ZoneOrSubCityOptions)
from app.services.anomaly_detector import AnomalyDetectorService  # noqa: E402


def plot_shap_waterfall(explanation, title="SHAP Feature Importance"):
    """
    Create a waterfall plot showing SHAP feature contributions
    """
    top_features = explanation.get("top_contributing_features", {})
    shap_values = explanation.get("shap_values", {})

    if not top_features:
        print("No SHAP explanation available")
        return

    # Get top features and their SHAP values
    feature_names = list(top_features.keys())
    importance_values = [top_features[f] for f in feature_names]
    shap_vals = [shap_values.get(f, 0) for f in feature_names]

    # Create horizontal bar plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color bars based on positive/negative contribution
    colors = ["red" if v < 0 else "green" for v in shap_vals]

    y_pos = np.arange(len(feature_names))
    ax.barh(y_pos, importance_values, color=colors, alpha=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(feature_names)
    ax.set_xlabel("SHAP Value (Importance)")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    return fig


async def visualize_kyc_example():
    """Visualize SHAP explanation for a KYC example"""
    print("\n" + "=" * 60)
    print("Visualizing SHAP Explanation for KYC Prediction")
    print("=" * 60)

    service = AnomalyDetectorService()
    await service.initialize()

    # Create test KYC data
    kyc_data = KYCData(
        customer_phone_number="974978374",
        customer_age=35,
        customer_gender=Gender.FEMALE,
        customer_marital_status=MaritalStatusOptions.MARRIED,
        customer_education_level=EducationalLevelOptions.TERTIARY,
        customer_tin_number="4108443882",
        customer_name="Test Customer",
        customer_bank_account_number="0486851428712",
        customer_region=RegionOptions.AFAR,
        customer_city=CityOptions.HARRAR,
        customer_zone_or_sub_city=ZoneOrSubCityOptions.ZONE_10,
        customer_woreda="15",
        customer_id="CUST_TEST_001",
    )

    # Get prediction with explanation
    is_anomaly, score, risk_level, explanation = service.predict_kyc(kyc_data)

    print(f"\nPrediction Results:")
    print(f"  Is Anomaly: {is_anomaly}")
    print(f"  Anomaly Score: {score:.4f}")
    print(f"  Risk Level: {risk_level}")

    print("\nTop Contributing Features:")
    for feature, importance in explanation.get("top_contributing_features", {}).items():
        shap_val = explanation["shap_values"].get(feature, 0)
        direction = "↑ increases" if shap_val > 0 else "↓ decreases"
        print(f"  {feature}: {importance:.4f} ({direction} anomaly score)")

    # Create visualization
    plot_shap_waterfall(
        explanation, title=f"SHAP Explanation for KYC (Score: {score:.3f})"
    )

    # Save plot
    output_path = "shap_kyc_example.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\n✅ Visualization saved to: {output_path}")

    plt.close()


async def visualize_transaction_example():
    """Visualize SHAP explanation for a Transaction example"""
    print("\n" + "=" * 60)
    print("Visualizing SHAP Explanation for Transaction Prediction")
    print("=" * 60)

    service = AnomalyDetectorService()
    await service.initialize()

    # Create test transaction data
    txn_data = TransactionData(
        customer_id="CUST_TEST_001",
        date="2024-01-15T02:30:00Z",  # Unusual hour
        credit=150000.0,  # Large amount
        debit=0.0,
        closingBalance=200000.0,
        narrative="CASH DEPOSIT LATE NIGHT",
        source="CASH DEPOSIT",
    )

    # Get prediction with explanation
    is_anomaly, score, risk_level, explanation = service.predict_transaction(txn_data)

    print(f"\nPrediction Results:")
    print(f"  Is Anomaly: {is_anomaly}")
    print(f"  Anomaly Score: {score:.4f}")
    print(f"  Risk Level: {risk_level}")

    print("\nTop Contributing Features:")
    for feature, importance in explanation.get("top_contributing_features", {}).items():
        shap_val = explanation["shap_values"].get(feature, 0)
        feat_val = explanation["feature_values"].get(feature, 0)
        direction = "↑ increases" if shap_val > 0 else "↓ decreases"
        print(
            f"  {feature}: {importance:.4f} (value={feat_val:.2f}, {direction} anomaly score)"
        )

    # Create visualization
    plot_shap_waterfall(
        explanation, title=f"SHAP Explanation for Transaction (Score: {score:.3f})"
    )

    # Save plot
    output_path = "shap_transaction_example.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\n✅ Visualization saved to: {output_path}")

    plt.close()


async def compare_predictions():
    """Compare SHAP explanations for normal vs anomalous predictions"""
    print("\n" + "=" * 60)
    print("Comparing Normal vs Anomalous Predictions")
    print("=" * 60)

    service = AnomalyDetectorService()
    await service.initialize()

    # Normal transaction
    normal_txn = TransactionData(
        customer_id="CUST_001",
        date="2024-01-15T14:30:00Z",
        credit=5000.0,
        debit=0.0,
        closingBalance=50000.0,
        narrative="Regular deposit",
        source="CASH DEPOSIT",
    )

    # Suspicious transaction
    suspicious_txn = TransactionData(
        customer_id="CUST_002",
        date="2024-01-15T03:00:00Z",  # Late night
        credit=250000.0,  # Very large amount
        debit=0.0,
        closingBalance=300000.0,
        narrative="X",  # Very short narrative
        source="CASH DEPOSIT",
    )

    # Get predictions
    normal_result = service.predict_transaction(normal_txn)
    suspicious_result = service.predict_transaction(suspicious_txn)

    print("\n📊 Comparison Results:")
    print("\nNormal Transaction:")
    print(f"  Score: {normal_result[1]:.4f}")
    print(f"  Risk: {normal_result[2]}")
    print(
        f"  Top Features: {list(normal_result[3]['top_contributing_features'].keys())[:3]}"
    )

    print("\nSuspicious Transaction:")
    print(f"  Score: {suspicious_result[1]:.4f}")
    print(f"  Risk: {suspicious_result[2]}")
    print(
        f"  Top Features: {list(suspicious_result[3]['top_contributing_features'].keys())[:3]}"
    )

    # Create side-by-side visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot normal
    exp1 = normal_result[3]
    features1 = list(exp1["top_contributing_features"].keys())
    values1 = [exp1["top_contributing_features"][f] for f in features1]
    shap1 = [exp1["shap_values"][f] for f in features1]
    colors1 = ["red" if v < 0 else "green" for v in shap1]

    ax1.barh(range(len(features1)), values1, color=colors1, alpha=0.6)
    ax1.set_yticks(range(len(features1)))
    ax1.set_yticklabels(features1)
    ax1.set_title(f"Normal Transaction\n(Score: {normal_result[1]:.3f})")
    ax1.set_xlabel("SHAP Importance")
    ax1.grid(axis="x", alpha=0.3)

    # Plot suspicious
    exp2 = suspicious_result[3]
    features2 = list(exp2["top_contributing_features"].keys())
    values2 = [exp2["top_contributing_features"][f] for f in features2]
    shap2 = [exp2["shap_values"][f] for f in features2]
    colors2 = ["red" if v < 0 else "green" for v in shap2]

    ax2.barh(range(len(features2)), values2, color=colors2, alpha=0.6)
    ax2.set_yticks(range(len(features2)))
    ax2.set_yticklabels(features2)
    ax2.set_title(f"Suspicious Transaction\n(Score: {suspicious_result[1]:.3f})")
    ax2.set_xlabel("SHAP Importance")
    ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()

    output_path = "shap_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\n✅ Comparison visualization saved to: {output_path}")

    plt.close()


async def main():
    """Run visualization examples"""
    try:
        # Example 1: KYC visualization
        await visualize_kyc_example()

        # Example 2: Transaction visualization
        await visualize_transaction_example()

        # Example 3: Comparison
        await compare_predictions()

        print("\n" + "=" * 60)
        print("✅ All visualizations completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
