"""
Download MovieLens 25M dataset
"""
import os
import requests
import zipfile
from tqdm import tqdm

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
DATA_DIR = "data"
EXTRACT_DIR = os.path.join(DATA_DIR, "ml-25m")

def download_file(url: str, destination: str):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f, tqdm(
        desc=destination,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def main():
    """Download and extract MovieLens 25M"""
    print("🎬 Downloading MovieLens 25M dataset...")
    
    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Check if already downloaded
    if os.path.exists(EXTRACT_DIR):
        print(f"✅ Dataset already exists at {EXTRACT_DIR}")
        return
    
    # Download
    zip_path = os.path.join(DATA_DIR, "ml-25m.zip")
    
    if not os.path.exists(zip_path):
        print(f"📥 Downloading from {MOVIELENS_URL}...")
        download_file(MOVIELENS_URL, zip_path)
        print(f"✅ Downloaded to {zip_path}")
    else:
        print(f"✅ Zip file already exists at {zip_path}")
    
    # Extract
    print(f"📦 Extracting to {DATA_DIR}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    
    print(f"✅ Extracted to {EXTRACT_DIR}")
    
    # Verify files
    required_files = ['ratings.csv', 'movies.csv', 'tags.csv', 'links.csv']
    for file in required_files:
        file_path = os.path.join(EXTRACT_DIR, file)
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   ✓ {file} ({size_mb:.1f} MB)")
        else:
            print(f"   ✗ {file} (missing)")
    
    print("\n🎉 MovieLens 25M dataset ready!")
    print(f"   Location: {EXTRACT_DIR}")
    print(f"   Next step: Run 'make train' to train ML models")

if __name__ == "__main__":
    main()
