"""
PDF archival system for storing and retrieving historical PDF snapshots.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from .models import PDFSnapshot, Prediction, PatternMatch
from .db_config import DatabaseManager, db_session


class PDFArchive:
    """
    Manages storage and retrieval of historical PDF snapshots.

    Provides high-level API for:
    - Storing new PDF snapshots
    - Retrieving historical snapshots
    - Querying by ticker, date range, expiration
    - Getting snapshots for pattern matching
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize PDF archive.

        Args:
            db_manager: DatabaseManager instance. If None, creates default.
        """
        self.db_manager = db_manager or DatabaseManager()

    def store_snapshot(
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
        timestamp: datetime = None
    ) -> PDFSnapshot:
        """
        Store a new PDF snapshot in the database.

        Args:
            ticker: Stock ticker (e.g., 'SPY')
            spot_price: Current spot price
            days_to_expiry: Days until expiration
            expiration_date: Option expiration date
            risk_free_rate: Risk-free rate used
            strikes: Array of strike prices
            pdf_values: Array of PDF values
            statistics: Dictionary of PDF statistics
            sabr_params: SABR parameters (alpha, rho, nu, beta)
            interpolation_method: Method used ('sabr' or 'spline')
            interpretation: AI interpretation text
            interpretation_mode: Mode used for interpretation
            model_used: Model used ('ollama' or 'fallback')
            timestamp: Snapshot timestamp (defaults to now)

        Returns:
            PDFSnapshot object
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Create snapshot
        snapshot = PDFSnapshot(
            timestamp=timestamp,
            ticker=ticker,
            spot_price=spot_price,
            days_to_expiry=days_to_expiry,
            expiration_date=expiration_date,
            risk_free_rate=risk_free_rate,
            interpolation_method=interpolation_method,
            interpretation=interpretation,
            interpretation_mode=interpretation_mode,
            model_used=model_used
        )

        # Set arrays
        snapshot.set_strikes(strikes)
        snapshot.set_pdf_values(pdf_values)
        snapshot.set_statistics(statistics)

        # Set SABR params if provided
        if sabr_params:
            snapshot.sabr_alpha = sabr_params.get('alpha')
            snapshot.sabr_rho = sabr_params.get('rho')
            snapshot.sabr_nu = sabr_params.get('nu')
            snapshot.sabr_beta = sabr_params.get('beta')

        # Save to database
        with self.db_manager.session_scope() as session:
            session.add(snapshot)
            session.flush()  # Get the ID
            snapshot_id = snapshot.id

        print(f"✅ Stored PDF snapshot: {ticker} @ {timestamp}, ID={snapshot_id}")
        return snapshot

    def get_snapshot_by_id(self, snapshot_id: int) -> Optional[PDFSnapshot]:
        """
        Retrieve a snapshot by ID.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            PDFSnapshot or None if not found
        """
        with db_session() as session:
            return session.query(PDFSnapshot).filter_by(id=snapshot_id).first()

    def get_latest_snapshot(
        self,
        ticker: str = 'SPY',
        days_to_expiry: int = None
    ) -> Optional[PDFSnapshot]:
        """
        Get the most recent snapshot for a ticker.

        Args:
            ticker: Stock ticker
            days_to_expiry: Filter by specific DTE (optional)

        Returns:
            Most recent PDFSnapshot or None
        """
        with db_session() as session:
            query = session.query(PDFSnapshot).filter_by(ticker=ticker)

            if days_to_expiry is not None:
                query = query.filter_by(days_to_expiry=days_to_expiry)

            snapshot = query.order_by(desc(PDFSnapshot.timestamp)).first()
            return snapshot

    def get_snapshots_by_date_range(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        days_to_expiry: int = None
    ) -> List[PDFSnapshot]:
        """
        Get all snapshots within a date range.

        Args:
            ticker: Stock ticker
            start_date: Start of date range
            end_date: End of date range
            days_to_expiry: Filter by specific DTE (optional)

        Returns:
            List of PDFSnapshot objects
        """
        with db_session() as session:
            query = session.query(PDFSnapshot).filter(
                and_(
                    PDFSnapshot.ticker == ticker,
                    PDFSnapshot.timestamp >= start_date,
                    PDFSnapshot.timestamp <= end_date
                )
            )

            if days_to_expiry is not None:
                query = query.filter_by(days_to_expiry=days_to_expiry)

            snapshots = query.order_by(PDFSnapshot.timestamp).all()
            return snapshots

    def get_snapshots_for_pattern_matching(
        self,
        ticker: str,
        exclude_recent_days: int = 7,
        min_snapshots: int = 10,
        max_snapshots: int = 100,
        days_to_expiry_range: Tuple[int, int] = (20, 40)
    ) -> List[Dict[str, Any]]:
        """
        Get historical snapshots suitable for pattern matching.

        Args:
            ticker: Stock ticker
            exclude_recent_days: Exclude snapshots from last N days
            min_snapshots: Minimum number of snapshots to return
            max_snapshots: Maximum number of snapshots to return
            days_to_expiry_range: (min_dte, max_dte) to filter by

        Returns:
            List of dictionaries with snapshot data for pattern matching
        """
        cutoff_date = datetime.utcnow() - timedelta(days=exclude_recent_days)

        with db_session() as session:
            query = session.query(PDFSnapshot).filter(
                and_(
                    PDFSnapshot.ticker == ticker,
                    PDFSnapshot.timestamp <= cutoff_date,
                    PDFSnapshot.days_to_expiry >= days_to_expiry_range[0],
                    PDFSnapshot.days_to_expiry <= days_to_expiry_range[1]
                )
            ).order_by(desc(PDFSnapshot.timestamp)).limit(max_snapshots)

            snapshots = query.all()

            # Convert to format expected by pattern matcher
            pattern_data = []
            for snapshot in snapshots:
                pattern_data.append({
                    'id': snapshot.id,
                    'date': snapshot.timestamp.strftime('%Y-%m-%d'),
                    'pdf': snapshot.get_pdf_values(),
                    'strikes': snapshot.get_strikes(),
                    'stats': snapshot.get_statistics(),
                    'spot': snapshot.spot_price,
                    'dte': snapshot.days_to_expiry
                })

            return pattern_data

    def store_pattern_matches(
        self,
        current_snapshot_id: int,
        matches: List[Dict[str, Any]]
    ):
        """
        Store pattern matching results.

        Args:
            current_snapshot_id: ID of current snapshot being analyzed
            matches: List of match dictionaries from PatternMatcher
        """
        with self.db_manager.session_scope() as session:
            for rank, match in enumerate(matches, start=1):
                pattern_match = PatternMatch(
                    current_snapshot_id=current_snapshot_id,
                    historical_snapshot_id=match.get('id'),
                    match_timestamp=datetime.utcnow(),
                    overall_similarity=match.get('similarity'),
                    shape_similarity=match.get('shape_similarity', match.get('similarity')),
                    stats_similarity=match.get('stats_similarity', match.get('similarity')),
                    match_rank=rank,
                    description=match.get('description')
                )
                session.add(pattern_match)

        print(f"✅ Stored {len(matches)} pattern matches for snapshot {current_snapshot_id}")

    def get_pattern_matches(
        self,
        snapshot_id: int,
        min_similarity: float = 0.0
    ) -> List[PatternMatch]:
        """
        Get pattern matches for a snapshot.

        Args:
            snapshot_id: Snapshot ID
            min_similarity: Minimum similarity threshold

        Returns:
            List of PatternMatch objects
        """
        with db_session() as session:
            matches = session.query(PatternMatch).filter(
                and_(
                    PatternMatch.current_snapshot_id == snapshot_id,
                    PatternMatch.overall_similarity >= min_similarity
                )
            ).order_by(PatternMatch.match_rank).all()

            return matches

    def store_prediction(
        self,
        snapshot_id: int,
        forecast_date: datetime,
        target_date: datetime,
        ticker: str,
        condition: str,
        target_level: float,
        predicted_probability: float,
        target_level_upper: float = None,
        notes: str = None
    ) -> Prediction:
        """
        Store a prediction made from a PDF.

        Args:
            snapshot_id: ID of snapshot used for prediction
            forecast_date: Date prediction was made
            target_date: Date to evaluate prediction
            ticker: Stock ticker
            condition: 'above', 'below', or 'between'
            target_level: Strike or price level
            predicted_probability: Forecasted probability (0-1)
            target_level_upper: Upper level for 'between' condition
            notes: Additional notes

        Returns:
            Prediction object
        """
        prediction = Prediction(
            snapshot_id=snapshot_id,
            forecast_date=forecast_date,
            target_date=target_date,
            ticker=ticker,
            condition=condition,
            target_level=target_level,
            target_level_upper=target_level_upper,
            predicted_probability=predicted_probability,
            notes=notes
        )

        with self.db_manager.session_scope() as session:
            session.add(prediction)
            session.flush()
            prediction_id = prediction.id

        print(f"✅ Stored prediction: {ticker} {condition} {target_level}, prob={predicted_probability:.2%}, ID={prediction_id}")
        return prediction

    def evaluate_prediction(
        self,
        prediction_id: int,
        actual_price: float,
        evaluation_date: datetime = None
    ) -> Prediction:
        """
        Evaluate a prediction with actual outcome.

        Args:
            prediction_id: Prediction ID
            actual_price: Actual price at target date
            evaluation_date: Date of evaluation (defaults to now)

        Returns:
            Updated Prediction object
        """
        if evaluation_date is None:
            evaluation_date = datetime.utcnow()

        with self.db_manager.session_scope() as session:
            prediction = session.query(Prediction).filter_by(id=prediction_id).first()

            if prediction is None:
                raise ValueError(f"Prediction {prediction_id} not found")

            # Determine if condition was met
            if prediction.condition == 'above':
                outcome = actual_price > prediction.target_level
            elif prediction.condition == 'below':
                outcome = actual_price < prediction.target_level
            elif prediction.condition == 'between':
                outcome = (prediction.target_level <= actual_price <= prediction.target_level_upper)
            else:
                raise ValueError(f"Unknown condition: {prediction.condition}")

            # Update prediction
            prediction.actual_price = actual_price
            prediction.actual_outcome = outcome
            prediction.evaluation_date = evaluation_date

            # Calculate Brier score
            prediction.calculate_brier_score()

            session.flush()

        print(f"✅ Evaluated prediction {prediction_id}: outcome={outcome}, brier={prediction.accuracy_score:.4f}")
        return prediction

    def get_pending_predictions(
        self,
        ticker: str = None,
        before_date: datetime = None
    ) -> List[Prediction]:
        """
        Get predictions that haven't been evaluated yet.

        Args:
            ticker: Filter by ticker (optional)
            before_date: Only get predictions with target_date before this

        Returns:
            List of unevaluated Prediction objects
        """
        if before_date is None:
            before_date = datetime.utcnow()

        with db_session() as session:
            query = session.query(Prediction).filter(
                and_(
                    Prediction.actual_outcome.is_(None),
                    Prediction.target_date <= before_date
                )
            )

            if ticker:
                query = query.filter_by(ticker=ticker)

            predictions = query.order_by(Prediction.target_date).all()
            return predictions

    def get_prediction_accuracy_stats(
        self,
        ticker: str = 'SPY',
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Calculate accuracy statistics for predictions.

        Args:
            ticker: Stock ticker
            start_date: Start of evaluation period
            end_date: End of evaluation period

        Returns:
            Dictionary with accuracy metrics
        """
        with db_session() as session:
            query = session.query(Prediction).filter(
                and_(
                    Prediction.ticker == ticker,
                    Prediction.actual_outcome.isnot(None)
                )
            )

            if start_date:
                query = query.filter(Prediction.evaluation_date >= start_date)
            if end_date:
                query = query.filter(Prediction.evaluation_date <= end_date)

            predictions = query.all()

            if not predictions:
                return {
                    'total_predictions': 0,
                    'evaluated_predictions': 0,
                    'mean_brier_score': None,
                    'calibration': None
                }

            # Calculate metrics
            total = len(predictions)
            correct = sum(1 for p in predictions if p.actual_outcome)
            brier_scores = [p.accuracy_score for p in predictions if p.accuracy_score is not None]

            return {
                'total_predictions': total,
                'correct_predictions': correct,
                'accuracy_rate': correct / total if total > 0 else 0,
                'mean_brier_score': np.mean(brier_scores) if brier_scores else None,
                'median_brier_score': np.median(brier_scores) if brier_scores else None,
                'predictions': [p.to_dict() for p in predictions]
            }

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get overall database statistics.

        Returns:
            Dictionary with database stats
        """
        with db_session() as session:
            total_snapshots = session.query(PDFSnapshot).count()
            total_predictions = session.query(Prediction).count()
            total_matches = session.query(PatternMatch).count()

            evaluated_predictions = session.query(Prediction).filter(
                Prediction.actual_outcome.isnot(None)
            ).count()

            # Get date range
            first_snapshot = session.query(PDFSnapshot).order_by(PDFSnapshot.timestamp).first()
            last_snapshot = session.query(PDFSnapshot).order_by(desc(PDFSnapshot.timestamp)).first()

            return {
                'total_snapshots': total_snapshots,
                'total_predictions': total_predictions,
                'evaluated_predictions': evaluated_predictions,
                'pending_predictions': total_predictions - evaluated_predictions,
                'total_pattern_matches': total_matches,
                'first_snapshot_date': first_snapshot.timestamp if first_snapshot else None,
                'last_snapshot_date': last_snapshot.timestamp if last_snapshot else None,
            }


if __name__ == "__main__":
    # Test PDF archive
    print("Testing PDF Archive...")

    # Create archive
    archive = PDFArchive()
    print("✅ Archive created")

    # Create test snapshot
    test_strikes = np.linspace(400, 500, 100)
    test_pdf = np.exp(-0.5 * ((test_strikes - 450) / 15)**2)
    test_pdf = test_pdf / np.trapz(test_pdf, test_strikes)

    test_stats = {
        'mean': 450.0,
        'std': 15.0,
        'skewness': -0.1,
        'excess_kurtosis': 0.3,
        'implied_move_pct': 3.5
    }

    # Store snapshot
    snapshot = archive.store_snapshot(
        ticker='SPY',
        spot_price=450.0,
        days_to_expiry=30,
        expiration_date=datetime.utcnow() + timedelta(days=30),
        risk_free_rate=0.05,
        strikes=test_strikes,
        pdf_values=test_pdf,
        statistics=test_stats,
        interpretation="Test interpretation"
    )
    print(f"✅ Stored snapshot: {snapshot}")

    # Retrieve snapshot
    retrieved = archive.get_snapshot_by_id(snapshot.id)
    print(f"✅ Retrieved snapshot: {retrieved}")

    # Get stats
    stats = archive.get_database_stats()
    print(f"✅ Database stats: {stats}")

    print("\n✅ All PDF archive tests passed!")
