"""
SQLAlchemy models for PDF storage and prediction tracking.
"""

from datetime import datetime
from typing import Dict, Any, List
import json
import pickle
import numpy as np

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Text, LargeBinary, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PDFSnapshot(Base):
    """
    Stores historical PDF snapshots with all associated data.

    Each snapshot represents the option-implied probability distribution
    at a specific point in time for a specific expiration.
    """
    __tablename__ = 'pdf_snapshots'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Timestamp and identification
    timestamp = Column(DateTime, nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)

    # Market data
    spot_price = Column(Float, nullable=False)
    days_to_expiry = Column(Integer, nullable=False)
    expiration_date = Column(DateTime, nullable=False)

    # Risk-free rate
    risk_free_rate = Column(Float, nullable=False)

    # PDF data (stored as binary)
    strikes = Column(LargeBinary, nullable=False)  # NumPy array pickled
    pdf_values = Column(LargeBinary, nullable=False)  # NumPy array pickled

    # SABR parameters (if used)
    sabr_alpha = Column(Float, nullable=True)
    sabr_rho = Column(Float, nullable=True)
    sabr_nu = Column(Float, nullable=True)
    sabr_beta = Column(Float, nullable=True)
    interpolation_method = Column(String(20), nullable=True)  # 'sabr' or 'spline'

    # Statistics (stored as JSON)
    statistics = Column(Text, nullable=False)  # JSON string

    # AI interpretation
    interpretation = Column(Text, nullable=True)
    interpretation_mode = Column(String(20), nullable=True)  # 'standard', 'conservative', etc.
    model_used = Column(String(50), nullable=True)  # 'ollama' or 'fallback'

    # Relationships
    pattern_matches = relationship('PatternMatch',
                                  foreign_keys='PatternMatch.current_snapshot_id',
                                  back_populates='current_snapshot')
    predictions = relationship('Prediction', back_populates='snapshot')

    # Indexes for common queries
    __table_args__ = (
        Index('idx_ticker_timestamp', 'ticker', 'timestamp'),
        Index('idx_ticker_expiry', 'ticker', 'days_to_expiry'),
    )

    def __repr__(self):
        return f"<PDFSnapshot(id={self.id}, ticker={self.ticker}, timestamp={self.timestamp}, dte={self.days_to_expiry})>"

    def get_strikes(self) -> np.ndarray:
        """Deserialize strikes from binary."""
        return pickle.loads(self.strikes)

    def set_strikes(self, strikes: np.ndarray):
        """Serialize strikes to binary."""
        self.strikes = pickle.dumps(strikes)

    def get_pdf_values(self) -> np.ndarray:
        """Deserialize PDF values from binary."""
        return pickle.loads(self.pdf_values)

    def set_pdf_values(self, pdf_values: np.ndarray):
        """Serialize PDF values to binary."""
        self.pdf_values = pickle.dumps(pdf_values)

    def get_statistics(self) -> Dict[str, Any]:
        """Deserialize statistics from JSON."""
        return json.loads(self.statistics)

    def set_statistics(self, stats: Dict[str, Any]):
        """Serialize statistics to JSON."""
        self.statistics = json.dumps(stats)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'ticker': self.ticker,
            'spot_price': self.spot_price,
            'days_to_expiry': self.days_to_expiry,
            'expiration_date': self.expiration_date.isoformat(),
            'risk_free_rate': self.risk_free_rate,
            'strikes': self.get_strikes().tolist(),
            'pdf_values': self.get_pdf_values().tolist(),
            'sabr_params': {
                'alpha': self.sabr_alpha,
                'rho': self.sabr_rho,
                'nu': self.sabr_nu,
                'beta': self.sabr_beta,
            },
            'interpolation_method': self.interpolation_method,
            'statistics': self.get_statistics(),
            'interpretation': self.interpretation,
            'interpretation_mode': self.interpretation_mode,
            'model_used': self.model_used,
        }


class Prediction(Base):
    """
    Tracks predictions made from PDFs and their outcomes.

    Used to evaluate the accuracy of option-implied probabilities
    by comparing forecasted probabilities with actual outcomes.
    """
    __tablename__ = 'predictions'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to PDF snapshot
    snapshot_id = Column(Integer, ForeignKey('pdf_snapshots.id'), nullable=False)

    # Forecast details
    forecast_date = Column(DateTime, nullable=False, index=True)
    target_date = Column(DateTime, nullable=False, index=True)
    ticker = Column(String(10), nullable=False)

    # Prediction
    condition = Column(String(20), nullable=False)  # 'above', 'below', 'between'
    target_level = Column(Float, nullable=False)  # Strike or price level
    target_level_upper = Column(Float, nullable=True)  # For 'between' condition
    predicted_probability = Column(Float, nullable=False)  # 0.0 to 1.0

    # Actual outcome
    evaluation_date = Column(DateTime, nullable=True)  # When we evaluated
    actual_price = Column(Float, nullable=True)  # Actual price at target_date
    actual_outcome = Column(Boolean, nullable=True)  # True if condition met

    # Accuracy metrics
    accuracy_score = Column(Float, nullable=True)  # Brier score or similar

    # Additional context
    notes = Column(Text, nullable=True)

    # Relationship
    snapshot = relationship('PDFSnapshot', back_populates='predictions')

    # Indexes
    __table_args__ = (
        Index('idx_ticker_target_date', 'ticker', 'target_date'),
    )

    def __repr__(self):
        return f"<Prediction(id={self.id}, ticker={self.ticker}, target_date={self.target_date}, prob={self.predicted_probability:.2%})>"

    def calculate_brier_score(self) -> float:
        """
        Calculate Brier score for this prediction.

        Brier Score = (predicted_prob - actual_outcome)^2
        Lower is better (0 = perfect forecast)
        """
        if self.actual_outcome is None:
            return None

        actual = 1.0 if self.actual_outcome else 0.0
        brier = (self.predicted_probability - actual) ** 2
        self.accuracy_score = brier
        return brier

    def to_dict(self) -> Dict[str, Any]:
        """Convert prediction to dictionary."""
        return {
            'id': self.id,
            'snapshot_id': self.snapshot_id,
            'forecast_date': self.forecast_date.isoformat(),
            'target_date': self.target_date.isoformat(),
            'ticker': self.ticker,
            'condition': self.condition,
            'target_level': self.target_level,
            'target_level_upper': self.target_level_upper,
            'predicted_probability': self.predicted_probability,
            'evaluation_date': self.evaluation_date.isoformat() if self.evaluation_date else None,
            'actual_price': self.actual_price,
            'actual_outcome': self.actual_outcome,
            'accuracy_score': self.accuracy_score,
            'notes': self.notes,
        }


class PatternMatch(Base):
    """
    Stores pattern matching results between current and historical PDFs.

    Used to find similar market conditions and compare outcomes.
    """
    __tablename__ = 'pattern_matches'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Current snapshot being analyzed
    current_snapshot_id = Column(Integer, ForeignKey('pdf_snapshots.id'), nullable=False)

    # Historical snapshot that matched
    historical_snapshot_id = Column(Integer, ForeignKey('pdf_snapshots.id'), nullable=False)

    # Match timestamp
    match_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Similarity scores
    overall_similarity = Column(Float, nullable=False)  # Combined score
    shape_similarity = Column(Float, nullable=False)  # Cosine similarity
    stats_similarity = Column(Float, nullable=False)  # Statistical features similarity

    # Match rank (1 = best match)
    match_rank = Column(Integer, nullable=False)

    # Description of historical pattern
    description = Column(Text, nullable=True)

    # Relationship
    current_snapshot = relationship('PDFSnapshot',
                                   foreign_keys=[current_snapshot_id],
                                   back_populates='pattern_matches')
    historical_snapshot = relationship('PDFSnapshot', foreign_keys=[historical_snapshot_id])

    # Indexes
    __table_args__ = (
        Index('idx_current_snapshot', 'current_snapshot_id'),
        Index('idx_similarity', 'overall_similarity'),
    )

    def __repr__(self):
        return f"<PatternMatch(current={self.current_snapshot_id}, historical={self.historical_snapshot_id}, sim={self.overall_similarity:.2%})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern match to dictionary."""
        return {
            'id': self.id,
            'current_snapshot_id': self.current_snapshot_id,
            'historical_snapshot_id': self.historical_snapshot_id,
            'match_timestamp': self.match_timestamp.isoformat(),
            'overall_similarity': self.overall_similarity,
            'shape_similarity': self.shape_similarity,
            'stats_similarity': self.stats_similarity,
            'match_rank': self.match_rank,
            'description': self.description,
        }


if __name__ == "__main__":
    # Print schema for documentation
    print("=" * 80)
    print("PDF VISUALIZER DATABASE SCHEMA")
    print("=" * 80)

    print("\nTABLE: pdf_snapshots")
    print("-" * 80)
    print("Stores historical PDF snapshots with all associated data")
    print("\nColumns:")
    for column in PDFSnapshot.__table__.columns:
        print(f"  - {column.name}: {column.type} {'(PK)' if column.primary_key else ''}")

    print("\n\nTABLE: predictions")
    print("-" * 80)
    print("Tracks predictions and their outcomes for accuracy evaluation")
    print("\nColumns:")
    for column in Prediction.__table__.columns:
        print(f"  - {column.name}: {column.type} {'(PK)' if column.primary_key else ''}")

    print("\n\nTABLE: pattern_matches")
    print("-" * 80)
    print("Stores pattern matching results between PDFs")
    print("\nColumns:")
    for column in PatternMatch.__table__.columns:
        print(f"  - {column.name}: {column.type} {'(PK)' if column.primary_key else ''}")

    print("\n" + "=" * 80)
