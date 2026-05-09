"""
Train Neural Collaborative Filtering (NCF) model on MovieLens 25M
"""
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

class NCFModel(nn.Module):
    """Neural Collaborative Filtering model"""
    
    def __init__(self, n_users: int, n_items: int, embedding_dim: int = 64):
        super().__init__()
        
        # User and item embeddings
        self.user_embedding = nn.Embedding(n_users, embedding_dim)
        self.item_embedding = nn.Embedding(n_items, embedding_dim)
        
        # MLP layers
        self.fc1 = nn.Linear(embedding_dim * 2, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
        # Initialize weights
        nn.init.normal_(self.user_embedding.weight, std=0.01)
        nn.init.normal_(self.item_embedding.weight, std=0.01)
    
    def forward(self, user_ids, item_ids):
        # Get embeddings
        user_emb = self.user_embedding(user_ids)
        item_emb = self.item_embedding(item_ids)
        
        # Concatenate
        x = torch.cat([user_emb, item_emb], dim=1)
        
        # MLP
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        
        return x.squeeze()

class RatingsDataset(Dataset):
    """PyTorch dataset for ratings"""
    
    def __init__(self, users, items, ratings):
        self.users = torch.LongTensor(users)
        self.items = torch.LongTensor(items)
        self.ratings = torch.FloatTensor(ratings)
    
    def __len__(self):
        return len(self.users)
    
    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.ratings[idx]

def train_ncf_model():
    """Train NCF model"""
    print("🚀 Starting NCF training...")
    
    # Load data
    data_path = "data/ml-25m/ratings.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"MovieLens data not found. Run 'make download-data' first.")
    
    print("📊 Loading MovieLens 25M dataset...")
    df = pd.read_csv(data_path)
    
    # Sample for faster training
    if len(df) > 1_000_000:
        print("   Sampling 1M ratings for faster training...")
        df = df.sample(n=1_000_000, random_state=42)
    
    # Create user/item mappings
    print("🔢 Creating user/item mappings...")
    user_ids = df['userId'].unique()
    item_ids = df['movieId'].unique()
    
    user_map = {uid: idx for idx, uid in enumerate(user_ids)}
    item_map = {iid: idx for idx, iid in enumerate(item_ids)}
    
    df['user_idx'] = df['userId'].map(user_map)
    df['item_idx'] = df['movieId'].map(item_map)
    
    n_users = len(user_ids)
    n_items = len(item_ids)
    
    print(f"   Users: {n_users:,}, Items: {n_items:,}")
    
    # Train/test split
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Create datasets
    train_dataset = RatingsDataset(
        train_df['user_idx'].values,
        train_df['item_idx'].values,
        train_df['rating'].values
    )
    
    test_dataset = RatingsDataset(
        test_df['user_idx'].values,
        test_df['item_idx'].values,
        test_df['rating'].values
    )
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=1024, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1024, shuffle=False)
    
    # Initialize model
    print("🧠 Initializing NCF model...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"   Using device: {device}")
    
    model = NCFModel(n_users, n_items, embedding_dim=64).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    n_epochs = 15
    print(f"\n🏋️ Training for {n_epochs} epochs...")
    
    for epoch in range(n_epochs):
        model.train()
        train_loss = 0.0
        
        for users, items, ratings in train_loader:
            users = users.to(device)
            items = items.to(device)
            ratings = ratings.to(device)
            
            optimizer.zero_grad()
            predictions = model(users, items)
            loss = criterion(predictions, ratings)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Evaluate
        model.eval()
        test_loss = 0.0
        
        with torch.no_grad():
            for users, items, ratings in test_loader:
                users = users.to(device)
                items = items.to(device)
                ratings = ratings.to(device)
                
                predictions = model(users, items)
                loss = criterion(predictions, ratings)
                test_loss += loss.item()
        
        train_rmse = np.sqrt(train_loss / len(train_loader))
        test_rmse = np.sqrt(test_loss / len(test_loader))
        
        print(f"   Epoch {epoch+1}/{n_epochs} - Train RMSE: {train_rmse:.4f}, Test RMSE: {test_rmse:.4f}")
    
    # Save model
    model_dir = "backend/app/ml/models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "ncf_v1.pt")
    
    print(f"\n💾 Saving model to {model_path}...")
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'n_users': n_users,
        'n_items': n_items,
        'user_map': user_map,
        'item_map': item_map,
        'test_rmse': test_rmse
    }, model_path)
    
    print(f"✅ NCF model trained successfully!")
    print(f"   Final Test RMSE: {test_rmse:.4f}")
    print(f"   Model saved to: {model_path}")
    
    return model

if __name__ == "__main__":
    train_ncf_model()
