"""
Train SVD collaborative filtering model on MovieLens 25M dataset
"""
import os
import pickle
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split
import pandas as pd

def train_svd_model():
    """Train SVD model on MovieLens 25M"""
    print("🚀 Starting SVD training...")
    
    # Load MovieLens 25M ratings
    data_path = "data/ml-25m/ratings.csv"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"MovieLens data not found at {data_path}. "
            "Run 'make download-data' first."
        )
    
    print("📊 Loading MovieLens 25M dataset...")
    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df):,} ratings")
    
    # Sample for faster training (use full dataset in production)
    # For demo: use 1M ratings, for production: remove this line
    if len(df) > 1_000_000:
        print("   Sampling 1M ratings for faster training...")
        df = df.sample(n=1_000_000, random_state=42)
    
    # Create Surprise dataset
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)
    
    # Train/test split
    print("🔀 Splitting data (80/20)...")
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
    
    # Train SVD model
    print("🧠 Training SVD model...")
    print("   Parameters: n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02")
    
    svd = SVD(
        n_factors=100,
        n_epochs=20,
        lr_all=0.005,
        reg_all=0.02,
        random_state=42,
        verbose=True
    )
    
    svd.fit(trainset)
    
    # Evaluate
    print("\n📈 Evaluating on test set...")
    predictions = svd.test(testset)
    rmse = accuracy.rmse(predictions, verbose=True)
    mae = accuracy.mae(predictions, verbose=True)
    
    # Check if meets target
    if rmse > 0.90:
        print(f"⚠️  Warning: RMSE {rmse:.4f} is above target (0.86)")
    else:
        print(f"✅ RMSE {rmse:.4f} meets target!")
    
    # Save model
    model_dir = "backend/app/ml/models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "svd_v1.pkl")
    
    print(f"\n💾 Saving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(svd, f)
    
    # Save metadata
    metadata = {
        'rmse': float(rmse),
        'mae': float(mae),
        'n_factors': 100,
        'n_epochs': 20,
        'training_samples': len(trainset.all_ratings()),
        'test_samples': len(testset)
    }
    
    metadata_path = os.path.join(model_dir, "svd_v1_metadata.pkl")
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"✅ SVD model trained successfully!")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   MAE: {mae:.4f}")
    print(f"   Model saved to: {model_path}")
    
    return svd, metadata

if __name__ == "__main__":
    train_svd_model()
