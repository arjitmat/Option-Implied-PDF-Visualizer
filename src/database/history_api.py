"""
High-level API for historical PDF data and predictions.

Provides a unified interface for:
- Storing PDF snapshots
- Retrieving historical data
- Pattern matching
- Prediction tracking
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from .db_config import DatabaseManager
from .pdf_archive import PDFArchive
from .vector_store import PDFVectorStore, HybridPatternMatcher


class HistoryAPI:
    """
    High-level API for PDF history and prediction tracking.

    This is the main interface that the Streamlit app will use
    for all database operations.
    """

    def __init__(
        self,
        db_manager: DatabaseManager = None,
        use_vector_store: bool = True
    ):
        """
        Initialize History API.

        Args:
            db_manager: DatabaseManager instance (creates default if None)
            use_vector_store: Whether to use ChromaDB for fast search
        """
        self.db_manager = db_manager or DatabaseManager()
        self.archive = PDFArchive(self.db_manager)

        # Initialize vector store if requested
        self.use_vector_store = use_vector_store
        if use_vector_store:
            self.vector_store = PDFVectorStore()
            self.hybrid_matcher = HybridPatternMatcher(
                self.vector_store,
                self.archive
            )
        else:
            self.vector_store = None
            self.hybrid_matcher = None

    # ========================================================================
    # PDF Snapshot Operations
    # ========================================================================

    def save_pdf_analysis(
        self,
        ticker: str,
        spot_price: float,
        days_to_expiry: int,
        expiration_date: datetime,
        risk_free_rate: float,
        strikes: np.ndarray,
        pdf_values: np.ndarray,
        statistics: Dict[str, Any],
        sabr_params: Dict[str, float] = None,
        interpolation_method: str = None,
        interpretation: str = None,
        interpretation_mode: str = None,
        model_used: str = None,
        store_in_vector_db: bool = True
    ) -> int:
        """
        Save a complete PDF analysis to the database.

        Args:
            ticker: Stock ticker
            spot_price: Current spot price
            days_to_expiry: Days to expiration
            expiration_date: Option expiration date
            risk_free_rate: Risk-free rate used
            strikes: Strike prices array
            pdf_values: PDF values array
            statistics: Dictionary of PDF statistics
            sabr_params: SABR parameters (optional)
            interpolation_method: Method used ('sabr' or 'spline')
            interpretation: AI interpretation text
            interpretation_mode: Mode used for interpretation
            model_used: Model used ('ollama' or 'fallback')
            store_in_vector_db: Whether to also store in ChromaDB

        Returns:
            Snapshot ID
        """
        # Store in SQLite
        snapshot = self.archive.store_snapshot(
            ticker=ticker,
            spot_price=spot_price,
            days_to_expiry=days_to_expiry,
            expiration_date=expiration_date,
            risk_free_rate=risk_free_rate,
            strikes=strikes,
            pdf_values=pdf_values,
            statistics=statistics,
            sabr_params=sabr_params,
            interpolation_method=interpolation_method,
            interpretation=interpretation,
            interpretation_mode=interpretation_mode,
            model_used=model_used
        )

        # Store in ChromaDB for fast similarity search
        if store_in_vector_db and self.vector_store:
            metadata = {
                'ticker': ticker,
                'date': snapshot.timestamp.strftime('%Y-%m-%d'),
                'spot': spot_price,
                'dte': days_to_expiry,
                **statistics
            }
            self.vector_store.add_snapshot(
                snapshot_id=snapshot.id,
                pdf=pdf_values,
                strikes=strikes,
                metadata=metadata
            )

        return snapshot.id

    def get_pdf_snapshot(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a PDF snapshot by ID.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            Dictionary with snapshot data or None
        """
        snapshot = self.archive.get_snapshot_by_id(snapshot_id)
        return snapshot.to_dict() if snapshot else None

    def get_latest_pdf(
        self,
        ticker: str = 'SPY',
        days_to_expiry: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent PDF for a ticker.

        Args:
            ticker: Stock ticker
            days_to_expiry: Filter by DTE (optional)

        Returns:
            Dictionary with snapshot data or None
        """
        snapshot = self.archive.get_latest_snapshot(ticker, days_to_expiry)
        return snapshot.to_dict() if snapshot else None

    def get_pdf_history(
        self,
        ticker: str,
        days: int = 30,
        days_to_expiry: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get PDF snapshots for the last N days.

        Args:
            ticker: Stock ticker
            days: Number of days to look back
            days_to_expiry: Filter by DTE (optional)

        Returns:
            List of snapshot dictionaries
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        snapshots = self.archive.get_snapshots_by_date_range(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            days_to_expiry=days_to_expiry
        )

        return [s.to_dict() for s in snapshots]

    # ========================================================================
    # Pattern Matching Operations
    # ========================================================================

    def find_similar_patterns(
        self,
        current_pdf: np.ndarray,
        current_strikes: np.ndarray,
        current_stats: Dict[str, Any],
        ticker: str = 'SPY',
        n_results: int = 10,
        min_similarity: float = 0.7,
        days_to_expiry_range: Tuple[int, int] = (20, 40)
    ) -> List[Dict[str, Any]]:
        """
        Find historically similar PDF patterns.

        Uses hybrid approach (ChromaDB + SQLite) if available,
        otherwise falls back to database-only search.

        Args:
            current_pdf: Current PDF values
            current_strikes: Current strikes
            current_stats: Current PDF statistics
            ticker: Stock ticker
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold
            days_to_expiry_range: Filter by DTE range

        Returns:
            List of similar patterns with similarity scores
        """
        if self.hybrid_matcher:
            # Use hybrid approach (fast)
            matches = self.hybrid_matcher.find_similar_patterns(
                current_pdf=current_pdf,
                current_strikes=current_strikes,
                current_stats=current_stats,
                ticker=ticker,
                n_results=n_results,
                min_similarity=min_similarity,
                days_to_expiry_range=days_to_expiry_range
            )
        else:
            # Fallback to database-only (slower but works)
            from src.core.patterns import PDFPatternMatcher

            historical_data = self.archive.get_snapshots_for_pattern_matching(
                ticker=ticker,
                max_snapshots=100,
                days_to_expiry_range=days_to_expiry_range
            )

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

    def save_pattern_matches(
        self,
        snapshot_id: int,
        matches: List[Dict[str, Any]]
    ):
        """
        Save pattern matching results to database.

        Args:
            snapshot_id: Current snapshot ID
            matches: List of match dictionaries
        """
        self.archive.store_pattern_matches(snapshot_id, matches)

    # ========================================================================
    # Prediction Tracking Operations
    # ========================================================================

    def create_prediction(
        self,
        snapshot_id: int,
        target_date: datetime,
        ticker: str,
        condition: str,
        target_level: float,
        predicted_probability: float,
        target_level_upper: float = None,
        notes: str = None
    ) -> int:
        """
        Create a prediction from a PDF snapshot.

        Args:
            snapshot_id: ID of snapshot used for prediction
            target_date: Date to evaluate prediction
            ticker: Stock ticker
            condition: 'above', 'below', or 'between'
            target_level: Strike or price level
            predicted_probability: Forecasted probability (0-1)
            target_level_upper: Upper level for 'between' condition
            notes: Additional notes

        Returns:
            Prediction ID
        """
        prediction = self.archive.store_prediction(
            snapshot_id=snapshot_id,
            forecast_date=datetime.utcnow(),
            target_date=target_date,
            ticker=ticker,
            condition=condition,
            target_level=target_level,
            predicted_probability=predicted_probability,
            target_level_upper=target_level_upper,
            notes=notes
        )

        return prediction.id

    def evaluate_prediction(
        self,
        prediction_id: int,
        actual_price: float
    ) -> Dict[str, Any]:
        """
        Evaluate a prediction with actual outcome.

        Args:
            prediction_id: Prediction ID
            actual_price: Actual price at target date

        Returns:
            Dictionary with prediction evaluation results
        """
        prediction = self.archive.evaluate_prediction(
            prediction_id=prediction_id,
            actual_price=actual_price
        )

        return prediction.to_dict()

    def get_pending_predictions(
        self,
        ticker: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get predictions that need to be evaluated.

        Args:
            ticker: Filter by ticker (optional)

        Returns:
            List of pending prediction dictionaries
        """
        predictions = self.archive.get_pending_predictions(ticker=ticker)
        return [p.to_dict() for p in predictions]

    def get_prediction_accuracy(
        self,
        ticker: str = 'SPY',
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Get prediction accuracy statistics.

        Args:
            ticker: Stock ticker
            days: Number of days to look back

        Returns:
            Dictionary with accuracy metrics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        return self.archive.get_prediction_accuracy_stats(
            ticker=ticker,
            start_date=start_date
        )

    # ========================================================================
    # Database Management
    # ========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall database statistics.

        Returns:
            Dictionary with database stats
        """
        db_stats = self.archive.get_database_stats()

        if self.vector_store:
            db_stats['vector_store_count'] = self.vector_store.get_count()

        return db_stats

    def clear_database(self, confirm: bool = False):
        """
        Clear all data from database (use with caution!).

        Args:
            confirm: Must be True to proceed
        """
        if not confirm:
            raise ValueError("Must set confirm=True to clear database")

        # Clear SQLite
        self.db_manager.drop_tables()
        self.db_manager.create_tables()

        # Clear ChromaDB
        if self.vector_store:
            self.vector_store.clear()

        print("⚠️  Database cleared!")

    def export_snapshot_to_dict(self, snapshot_id: int) -> Dict[str, Any]:
        """
        Export a snapshot to a complete dictionary (for backup/export).

        Args:
            snapshot_id: Snapshot ID

        Returns:
            Complete snapshot data as dictionary
        """
        return self.get_pdf_snapshot(snapshot_id)


# Convenience singleton for global access
_api_instance = None


def get_history_api() -> HistoryAPI:
    """
    Get the global HistoryAPI instance.

    Returns:
        HistoryAPI singleton
    """
    global _api_instance
    if _api_instance is None:
        _api_instance = HistoryAPI()
    return _api_instance


if __name__ == "__main__":
    # Test History API
    print("Testing History API...")

    # Create API
    api = HistoryAPI(use_vector_store=True)
    print("✅ History API created")

    # Create test data
    ticker = 'SPY'
    spot = 450.0
    dte = 30
    exp_date = datetime.utcnow() + timedelta(days=dte)
    r = 0.05

    strikes = np.linspace(400, 500, 100)
    pdf = np.exp(-0.5 * ((strikes - spot) / 15)**2)
    pdf = pdf / np.trapz(pdf, strikes)

    stats = {
        'mean': 450.5,
        'std': 15.0,
        'skewness': -0.1,
        'excess_kurtosis': 0.3,
        'implied_move_pct': 3.5,
        'prob_up_5pct': 0.25,
        'prob_down_5pct': 0.20
    }

    # Save PDF analysis
    snapshot_id = api.save_pdf_analysis(
        ticker=ticker,
        spot_price=spot,
        days_to_expiry=dte,
        expiration_date=exp_date,
        risk_free_rate=r,
        strikes=strikes,
        pdf_values=pdf,
        statistics=stats,
        interpretation="Test interpretation",
        model_used="test"
    )
    print(f"✅ Saved PDF analysis: ID={snapshot_id}")

    # Retrieve snapshot
    retrieved = api.get_pdf_snapshot(snapshot_id)
    print(f"✅ Retrieved snapshot: {retrieved['ticker']} @ {retrieved['timestamp']}")

    # Get latest
    latest = api.get_latest_pdf(ticker)
    print(f"✅ Latest PDF: ID={latest['id']}")

    # Create prediction
    pred_id = api.create_prediction(
        snapshot_id=snapshot_id,
        target_date=exp_date,
        ticker=ticker,
        condition='above',
        target_level=455.0,
        predicted_probability=0.35,
        notes="Test prediction"
    )
    print(f"✅ Created prediction: ID={pred_id}")

    # Get database stats
    stats = api.get_stats()
    print(f"✅ Database stats:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")

    print("\n✅ All History API tests passed!")
