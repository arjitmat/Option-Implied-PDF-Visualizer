"""
ChromaDB vector store for fast PDF similarity search.

Uses vector embeddings of PDFs for efficient similarity search across
thousands of historical snapshots.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import json

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not installed. Vector search will be unavailable.")
    print("   Install with: pip install chromadb")


class PDFVectorStore:
    """
    Vector store for PDF embeddings using ChromaDB.

    Stores PDF arrays as embeddings for fast similarity search.
    Falls back gracefully if ChromaDB is not available.
    """

    def __init__(self, persist_directory: str = None):
        """
        Initialize vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data.
                             If None, uses default location.
        """
        self.available = CHROMADB_AVAILABLE

        if not self.available:
            print("⚠️  PDFVectorStore initialized but ChromaDB unavailable")
            self.client = None
            self.collection = None
            return

        # Set up persistence directory
        if persist_directory is None:
            project_root = Path(__file__).parent.parent.parent
            persist_directory = str(project_root / 'data' / 'chromadb')

        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="pdf_snapshots",
            metadata={"description": "Option-implied PDF snapshots"}
        )

        print(f"✅ ChromaDB vector store initialized: {persist_directory}")

    def _normalize_pdf(self, pdf: np.ndarray) -> np.ndarray:
        """
        Normalize PDF for embedding storage.

        Args:
            pdf: PDF array

        Returns:
            Normalized PDF (unit norm)
        """
        # Ensure it's a probability distribution
        pdf = pdf / np.sum(pdf)

        # Normalize to unit norm for cosine similarity
        norm = np.linalg.norm(pdf)
        if norm > 0:
            pdf = pdf / norm

        return pdf

    def _create_embedding(self, pdf: np.ndarray, strikes: np.ndarray) -> List[float]:
        """
        Create embedding from PDF.

        For now, we use the normalized PDF directly as the embedding.
        Could be enhanced with dimensionality reduction (PCA, etc.)

        Args:
            pdf: PDF values
            strikes: Strike prices

        Returns:
            Embedding as list of floats
        """
        # Normalize PDF
        embedding = self._normalize_pdf(pdf)

        # Convert to list for ChromaDB
        return embedding.tolist()

    def add_snapshot(
        self,
        snapshot_id: int,
        pdf: np.ndarray,
        strikes: np.ndarray,
        metadata: Dict[str, Any]
    ):
        """
        Add a PDF snapshot to the vector store.

        Args:
            snapshot_id: Database ID of snapshot
            pdf: PDF values
            strikes: Strike prices
            metadata: Additional metadata (ticker, date, stats, etc.)
        """
        if not self.available:
            return

        # Create embedding
        embedding = self._create_embedding(pdf, strikes)

        # Store in ChromaDB
        self.collection.add(
            embeddings=[embedding],
            documents=[json.dumps(metadata)],
            ids=[str(snapshot_id)]
        )

    def add_snapshots_batch(
        self,
        snapshots: List[Dict[str, Any]]
    ):
        """
        Add multiple snapshots at once (more efficient).

        Args:
            snapshots: List of dicts with keys: id, pdf, strikes, metadata
        """
        if not self.available:
            return

        embeddings = []
        documents = []
        ids = []

        for snapshot in snapshots:
            embedding = self._create_embedding(
                snapshot['pdf'],
                snapshot['strikes']
            )
            embeddings.append(embedding)
            documents.append(json.dumps(snapshot.get('metadata', {})))
            ids.append(str(snapshot['id']))

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids
        )

        print(f"✅ Added {len(snapshots)} snapshots to vector store")

    def find_similar(
        self,
        pdf: np.ndarray,
        strikes: np.ndarray,
        n_results: int = 10,
        min_similarity: float = 0.0,
        where: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar PDFs using vector similarity search.

        Args:
            pdf: Query PDF
            strikes: Query strikes
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)
            where: Filter conditions (e.g., {"ticker": "SPY"})

        Returns:
            List of similar snapshots with similarity scores
        """
        if not self.available:
            print("⚠️  ChromaDB unavailable, cannot search")
            return []

        # Create query embedding
        query_embedding = self._create_embedding(pdf, strikes)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        # Format results
        similar_snapshots = []
        for i, snapshot_id in enumerate(results['ids'][0]):
            distance = results['distances'][0][i]

            # Convert distance to similarity (cosine similarity)
            # ChromaDB uses L2 distance, convert to cosine similarity
            # For normalized vectors: cos_sim = 1 - (distance^2 / 2)
            similarity = 1 - (distance ** 2 / 2)

            if similarity >= min_similarity:
                metadata = json.loads(results['documents'][0][i])
                similar_snapshots.append({
                    'id': int(snapshot_id),
                    'similarity': similarity,
                    'distance': distance,
                    'metadata': metadata
                })

        return similar_snapshots

    def delete_snapshot(self, snapshot_id: int):
        """
        Remove a snapshot from the vector store.

        Args:
            snapshot_id: Database ID of snapshot
        """
        if not self.available:
            return

        self.collection.delete(ids=[str(snapshot_id)])

    def get_count(self) -> int:
        """
        Get total number of snapshots in vector store.

        Returns:
            Count of snapshots
        """
        if not self.available:
            return 0

        return self.collection.count()

    def persist(self):
        """Persist the vector store to disk."""
        if not self.available:
            return

        self.client.persist()
        print("✅ Vector store persisted to disk")

    def clear(self):
        """Clear all data from vector store (use with caution!)."""
        if not self.available:
            return

        # Delete collection and recreate
        self.client.delete_collection("pdf_snapshots")
        self.collection = self.client.create_collection(
            name="pdf_snapshots",
            metadata={"description": "Option-implied PDF snapshots"}
        )
        print("⚠️  Vector store cleared")


class HybridPatternMatcher:
    """
    Combines ChromaDB vector search with SQLite relational queries
    for efficient pattern matching.

    Uses ChromaDB for fast initial retrieval, then SQLite for
    detailed filtering and statistical comparison.
    """

    def __init__(self, vector_store: PDFVectorStore, pdf_archive):
        """
        Initialize hybrid matcher.

        Args:
            vector_store: PDFVectorStore instance
            pdf_archive: PDFArchive instance
        """
        self.vector_store = vector_store
        self.pdf_archive = pdf_archive

    def find_similar_patterns(
        self,
        current_pdf: np.ndarray,
        current_strikes: np.ndarray,
        current_stats: Dict[str, Any],
        ticker: str = 'SPY',
        n_candidates: int = 50,
        n_results: int = 10,
        min_similarity: float = 0.7,
        days_to_expiry_range: Tuple[int, int] = (20, 40)
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical patterns using hybrid approach.

        1. Fast vector search to get candidates (ChromaDB)
        2. Detailed statistical comparison on candidates (in-memory)
        3. Return top matches

        Args:
            current_pdf: Current PDF values
            current_strikes: Current strike prices
            current_stats: Current PDF statistics
            ticker: Stock ticker
            n_candidates: Number of candidates from vector search
            n_results: Final number of results to return
            min_similarity: Minimum similarity threshold
            days_to_expiry_range: Filter by DTE range

        Returns:
            List of similar patterns with scores
        """
        # If ChromaDB unavailable, fall back to database-only search
        if not self.vector_store.available:
            print("⚠️  ChromaDB unavailable, using database-only search")
            return self._fallback_search(
                current_pdf, current_strikes, current_stats,
                ticker, n_results, min_similarity, days_to_expiry_range
            )

        # Step 1: Vector search for candidates
        candidates = self.vector_store.find_similar(
            pdf=current_pdf,
            strikes=current_strikes,
            n_results=n_candidates,
            min_similarity=0.5,  # Lower threshold for candidates
            where={"ticker": ticker}
        )

        if not candidates:
            print("⚠️  No candidates found in vector search")
            return []

        # Step 2: Get full snapshot data for candidates
        candidate_ids = [c['id'] for c in candidates]
        candidate_snapshots = []

        for cid in candidate_ids:
            snapshot = self.pdf_archive.get_snapshot_by_id(cid)
            if snapshot and days_to_expiry_range[0] <= snapshot.days_to_expiry <= days_to_expiry_range[1]:
                candidate_snapshots.append({
                    'id': snapshot.id,
                    'date': snapshot.timestamp.strftime('%Y-%m-%d'),
                    'pdf': snapshot.get_pdf_values(),
                    'strikes': snapshot.get_strikes(),
                    'stats': snapshot.get_statistics(),
                    'spot': snapshot.spot_price,
                    'dte': snapshot.days_to_expiry
                })

        # Step 3: Detailed comparison using pattern matcher
        from src.core.patterns import PDFPatternMatcher
        matcher = PDFPatternMatcher(
            similarity_threshold=min_similarity,
            max_matches=n_results
        )

        matches = matcher.find_similar_patterns(
            current_pdf=current_pdf,
            current_strikes=current_strikes,
            current_stats=current_stats,
            historical_data=candidate_snapshots
        )

        return matches

    def _fallback_search(
        self,
        current_pdf: np.ndarray,
        current_strikes: np.ndarray,
        current_stats: Dict[str, Any],
        ticker: str,
        n_results: int,
        min_similarity: float,
        days_to_expiry_range: Tuple[int, int]
    ) -> List[Dict[str, Any]]:
        """
        Fallback pattern matching using only database.

        Uses PDFPatternMatcher with all historical snapshots.
        """
        # Get historical data from database
        historical_data = self.pdf_archive.get_snapshots_for_pattern_matching(
            ticker=ticker,
            max_snapshots=100,
            days_to_expiry_range=days_to_expiry_range
        )

        # Use pattern matcher
        from src.core.patterns import PDFPatternMatcher
        matcher = PDFPatternMatcher(
            similarity_threshold=min_similarity,
            max_matches=n_results
        )

        matches = matcher.find_similar_patterns(
            current_pdf=current_pdf,
            current_strikes=current_strikes,
            current_stats=current_stats,
            historical_data=historical_data
        )

        return matches


if __name__ == "__main__":
    # Test vector store
    if CHROMADB_AVAILABLE:
        print("Testing ChromaDB Vector Store...")

        # Create vector store
        vector_store = PDFVectorStore()
        print(f"✅ Vector store created, count: {vector_store.get_count()}")

        # Create test PDFs
        strikes = np.linspace(400, 500, 100)
        pdf1 = np.exp(-0.5 * ((strikes - 450) / 15)**2)
        pdf1 = pdf1 / np.trapz(pdf1, strikes)

        pdf2 = np.exp(-0.5 * ((strikes - 451) / 14)**2)
        pdf2 = pdf2 / np.trapz(pdf2, strikes)

        # Add snapshots
        vector_store.add_snapshot(
            snapshot_id=1,
            pdf=pdf1,
            strikes=strikes,
            metadata={'ticker': 'SPY', 'date': '2024-01-01'}
        )

        vector_store.add_snapshot(
            snapshot_id=2,
            pdf=pdf2,
            strikes=strikes,
            metadata={'ticker': 'SPY', 'date': '2024-01-02'}
        )

        print(f"✅ Added 2 snapshots, count: {vector_store.get_count()}")

        # Search for similar
        similar = vector_store.find_similar(
            pdf=pdf1,
            strikes=strikes,
            n_results=5
        )

        print(f"✅ Found {len(similar)} similar snapshots")
        for s in similar:
            print(f"   - ID {s['id']}: similarity={s['similarity']:.2%}")

        # Persist
        vector_store.persist()

        print("\n✅ All vector store tests passed!")
    else:
        print("⚠️  ChromaDB not available, skipping tests")
