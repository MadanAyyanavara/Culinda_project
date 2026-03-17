"""
Deduplication service using simple text similarity
"""
from typing import List, Tuple
import re
import hashlib
import logging

logger = logging.getLogger(__name__)


class DeduplicationService:
    """Service for detecting duplicate news items using simple similarity"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _tokenize(self, text: str) -> set:
        """Tokenize text into word set"""
        normalized = self._normalize_text(text)
        words = normalized.split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        return set(w for w in words if w not in stop_words and len(w) > 2)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts"""
        tokens1 = self._tokenize(text1)
        tokens2 = self._tokenize(text2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def find_duplicates(self, texts: List[str]) -> List[Tuple[int, int, float]]:
        """
        Find duplicate texts using Jaccard similarity.
        
        Returns list of tuples: (index1, index2, similarity_score)
        """
        if len(texts) < 2:
            return []
        
        try:
            duplicates = []
            n = len(texts)
            
            for i in range(n):
                for j in range(i + 1, n):
                    score = self._jaccard_similarity(texts[i], texts[j])
                    if score >= self.similarity_threshold:
                        duplicates.append((i, j, float(score)))
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Error in deduplication: {e}")
            return []
    
    def is_duplicate(self, text1: str, text2: str) -> Tuple[bool, float]:
        """
        Check if two texts are duplicates.
        
        Returns: (is_duplicate, similarity_score)
        """
        try:
            score = self._jaccard_similarity(text1, text2)
            return score >= self.similarity_threshold, float(score)
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return False, 0.0
    
    def cluster_similar(self, texts: List[str], n_clusters: int = None) -> List[int]:
        """
        Simple clustering based on similarity.
        
        Returns list of cluster IDs for each text.
        """
        if len(texts) < 2:
            return [0] * len(texts)
        
        try:
            # Simple greedy clustering
            clusters = []
            cluster_id = 0
            assigned = [False] * len(texts)
            
            for i in range(len(texts)):
                if assigned[i]:
                    continue
                
                # Start new cluster
                clusters.append([i])
                assigned[i] = True
                
                # Find similar texts
                for j in range(i + 1, len(texts)):
                    if not assigned[j]:
                        score = self._jaccard_similarity(texts[i], texts[j])
                        if score >= self.similarity_threshold * 0.8:  # Slightly lower threshold for clustering
                            clusters[-1].append(j)
                            assigned[j] = True
                
                cluster_id += 1
            
            # Create result array
            result = [0] * len(texts)
            for cid, cluster in enumerate(clusters):
                for idx in cluster:
                    result[idx] = cid
            
            return result
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return [0] * len(texts)


class ContentHasher:
    """Helper class for content hashing"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    @staticmethod
    def compute_hash(text: str) -> str:
        """Compute hash of normalized text"""
        normalized = ContentHasher.normalize_text(text)
        return hashlib.sha256(normalized.encode()).hexdigest()
