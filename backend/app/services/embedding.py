from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingService:
    """Sentence transformer embedding service"""
    
    def __init__(self):
        # Load model once at startup
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        print(f"✅ Loaded sentence-transformers model (dim={self.dimension})")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode single text to embedding"""
        return self.encode([text])[0]
