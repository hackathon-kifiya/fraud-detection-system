"""
Training Module CLI Entry Point
Allows running training modules directly via: python -m app.ml.training
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(
        description="Train anomaly detection models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train all unsupervised models
  python -m app.ml.training --mode unsupervised
  
  # Train all supervised models
  python -m app.ml.training --mode supervised
  
  # Train both
  python -m app.ml.training --mode all
  
  # Train specific model
  python -m app.ml.training --mode unsupervised --model transaction
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["unsupervised", "supervised", "all"],
        default="all",
        help="Training mode: unsupervised, supervised, or all (default: all)"
    )
    
    parser.add_argument(
        "--model",
        choices=["transaction", "merged", "customer", "all"],
        default="all",
        help="Specific model to train (default: all)"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/raw",
        help="Directory containing training data (default: data/raw)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/models",
        help="Directory to save trained models (default: data/models)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Import training modules
    from app.ml.training.train_unsupervised import train_unsupervised_models
    from app.ml.training.training_supervised import train_supervised_models
    
    print("=" * 70)
    print("ANOMALY DETECTION MODEL TRAINING")
    print("=" * 70)
    print(f"Mode: {args.mode}")
    print(f"Model: {args.model}")
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print("=" * 70)
    
    try:
        if args.mode in ["unsupervised", "all"]:
            print("\n[UNSUPERVISED TRAINING]")
            train_unsupervised_models()
        
        if args.mode in ["supervised", "all"]:
            print("\n[SUPERVISED TRAINING]")
            train_supervised_models()
        
        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

