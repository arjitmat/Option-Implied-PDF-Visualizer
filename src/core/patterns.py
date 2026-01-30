"""
Historical pattern matching for option-implied PDFs.

Find similar PDF shapes from historical data using cosine similarity
and statistical feature matching.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.spatial.distance import cosine
from scipy.stats import pearsonr
from config.constants import PATTERN_SIMILARITY_THRESHOLD, MAX_HISTORICAL_MATCHES


class PDFPatternMatcher:
    """
    Match current PDF patterns to historical PDFs.

    Uses multiple similarity measures:
    - Cosine similarity of PDF shape
    - Statistical feature similarity (mean, std, skew, kurtosis)
    - Combined weighted score
    """

    def __init__(
        self,
        similarity_threshold: float = PATTERN_SIMILARITY_THRESHOLD,
        max_matches: int = MAX_HISTORICAL_MATCHES
    ):
        """
        Initialize pattern matcher.

        Args:
            similarity_threshold: Minimum similarity score to return (0-1)
            max_matches: Maximum number of matches to return
        """
        self.similarity_threshold = similarity_threshold
        self.max_matches = max_matches

    def find_similar_patterns(
        self,
        current_pdf: np.ndarray,
        current_strikes: np.ndarray,
        current_stats: Dict[str, float],
        historical_data: List[Dict]
    ) -> List[Dict]:
        """
        Find historical PDFs similar to current PDF.

        Args:
            current_pdf: Current PDF values
            current_strikes: Current strike prices
            current_stats: Current PDF statistics
            historical_data: List of historical PDF data dicts with keys:
                - 'pdf': PDF values
                - 'strikes': Strike prices
                - 'stats': Statistics dict
                - 'date': Date string
                - 'metadata': Optional additional info

        Returns:
            List of similar patterns, sorted by similarity (best first)
        """
        if not historical_data:
            return []

        matches = []

        for hist_data in historical_data:
            # Calculate similarity
            similarity_score = self._calculate_similarity(
                current_pdf=current_pdf,
                current_strikes=current_strikes,
                current_stats=current_stats,
                hist_pdf=hist_data['pdf'],
                hist_strikes=hist_data['strikes'],
                hist_stats=hist_data['stats']
            )

            # Only include if above threshold
            if similarity_score >= self.similarity_threshold:
                match = {
                    'date': hist_data['date'],
                    'similarity': similarity_score,
                    'stats': hist_data['stats'],
                    'metadata': hist_data.get('metadata', {}),
                    'description': self._generate_description(hist_data)
                }

                matches.append(match)

        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)

        # Return top matches
        return matches[:self.max_matches]

    def _calculate_similarity(
        self,
        current_pdf: np.ndarray,
        current_strikes: np.ndarray,
        current_stats: Dict[str, float],
        hist_pdf: np.ndarray,
        hist_strikes: np.ndarray,
        hist_stats: Dict[str, float]
    ) -> float:
        """
        Calculate combined similarity score.

        Args:
            current_pdf, current_strikes, current_stats: Current PDF data
            hist_pdf, hist_strikes, hist_stats: Historical PDF data

        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # 1. PDF Shape Similarity (cosine similarity)
        shape_sim = self._pdf_shape_similarity(
            current_pdf, current_strikes,
            hist_pdf, hist_strikes
        )

        # 2. Statistical Feature Similarity
        stats_sim = self._stats_similarity(current_stats, hist_stats)

        # 3. Combined score (weighted average)
        # Shape is more important than stats
        combined_score = 0.7 * shape_sim + 0.3 * stats_sim

        return combined_score

    def _pdf_shape_similarity(
        self,
        pdf1: np.ndarray,
        strikes1: np.ndarray,
        pdf2: np.ndarray,
        strikes2: np.ndarray
    ) -> float:
        """
        Calculate shape similarity using cosine similarity.

        Interpolates PDFs to common grid for comparison.

        Args:
            pdf1, strikes1: First PDF
            pdf2, strikes2: Second PDF

        Returns:
            Cosine similarity (0-1)
        """
        # Find common strike range
        min_strike = max(strikes1.min(), strikes2.min())
        max_strike = min(strikes1.max(), strikes2.max())

        # Create common grid
        common_grid = np.linspace(min_strike, max_strike, 100)

        # Interpolate both PDFs to common grid
        pdf1_interp = np.interp(common_grid, strikes1, pdf1)
        pdf2_interp = np.interp(common_grid, strikes2, pdf2)

        # Normalize (ensure they sum to 1 over grid)
        pdf1_norm = pdf1_interp / np.trapz(pdf1_interp, common_grid)
        pdf2_norm = pdf2_interp / np.trapz(pdf2_interp, common_grid)

        # Calculate cosine similarity
        # (1 - cosine distance) since cosine distance is 0 for identical vectors
        try:
            similarity = 1 - cosine(pdf1_norm, pdf2_norm)
        except:
            similarity = 0.0

        # Ensure in [0, 1] range
        return max(0.0, min(1.0, similarity))

    def _stats_similarity(
        self,
        stats1: Dict[str, float],
        stats2: Dict[str, float]
    ) -> float:
        """
        Calculate similarity of statistical features.

        Compares: mean, std, skewness, kurtosis, implied_move

        Args:
            stats1, stats2: Statistics dictionaries

        Returns:
            Similarity score (0-1)
        """
        # Features to compare
        features = ['skewness', 'excess_kurtosis', 'implied_move_pct']

        similarities = []

        for feature in features:
            if feature in stats1 and feature in stats2:
                val1 = stats1[feature]
                val2 = stats2[feature]

                # Normalize difference to [0, 1] similarity
                # Using exponential decay: sim = exp(-|diff| / scale)
                if feature in ['skewness', 'excess_kurtosis']:
                    scale = 1.0  # Typical range
                else:  # implied_move_pct
                    scale = 5.0  # Percentage points

                diff = abs(val1 - val2)
                sim = np.exp(-diff / scale)
                similarities.append(sim)

        # Average similarity across features
        if similarities:
            return np.mean(similarities)
        else:
            return 0.5  # Neutral if no comparable features

    def _generate_description(self, hist_data: Dict) -> str:
        """
        Generate human-readable description of historical match.

        Args:
            hist_data: Historical data dict

        Returns:
            Description string
        """
        stats = hist_data['stats']
        metadata = hist_data.get('metadata', {})

        # Build description
        parts = []

        # Skewness description
        skew = stats.get('skewness', 0)
        if skew < -0.3:
            parts.append("heavy left tail")
        elif skew > 0.3:
            parts.append("heavy right tail")
        else:
            parts.append("symmetric")

        # Volatility level
        impl_move = stats.get('implied_move_pct', 0)
        if impl_move > 4:
            parts.append("high volatility")
        elif impl_move < 2:
            parts.append("low volatility")
        else:
            parts.append("moderate volatility")

        # Add any custom metadata
        if 'event' in metadata:
            parts.append(f"({metadata['event']})")

        return ", ".join(parts)


def calculate_pattern_score(
    current_pdf: np.ndarray,
    current_strikes: np.ndarray,
    historical_pdf: np.ndarray,
    historical_strikes: np.ndarray
) -> float:
    """
    Convenience function to calculate pattern similarity score.

    Args:
        current_pdf, current_strikes: Current PDF
        historical_pdf, historical_strikes: Historical PDF

    Returns:
        Similarity score (0-1)
    """
    matcher = PDFPatternMatcher()

    return matcher._pdf_shape_similarity(
        current_pdf, current_strikes,
        historical_pdf, historical_strikes
    )


if __name__ == "__main__":
    # Test pattern matching
    print("Testing PDF Pattern Matcher...\n")

    from scipy.stats import norm

    # Create synthetic current PDF
    spot = 450.0
    current_strikes = np.linspace(400, 500, 100)
    current_pdf = norm.pdf(current_strikes, loc=spot, scale=15)
    current_stats = {
        'skewness': -0.15,
        'excess_kurtosis': 0.5,
        'implied_move_pct': 3.38
    }

    # Create synthetic historical data
    historical_data = []

    # Similar pattern (should match well)
    hist_strikes1 = np.linspace(400, 500, 100)
    hist_pdf1 = norm.pdf(hist_strikes1, loc=451, scale=14.5)  # Very similar
    historical_data.append({
        'date': '2023-10-15',
        'pdf': hist_pdf1,
        'strikes': hist_strikes1,
        'stats': {
            'skewness': -0.14,
            'excess_kurtosis': 0.48,
            'implied_move_pct': 3.25
        },
        'metadata': {'event': 'Pre-earnings'}
    })

    # Different pattern (should not match well)
    hist_strikes2 = np.linspace(400, 500, 100)
    hist_pdf2 = norm.pdf(hist_strikes2, loc=455, scale=25)  # Very different
    historical_data.append({
        'date': '2023-08-20',
        'pdf': hist_pdf2,
        'strikes': hist_strikes2,
        'stats': {
            'skewness': 0.25,
            'excess_kurtosis': 1.2,
            'implied_move_pct': 6.5
        },
        'metadata': {'event': 'High volatility period'}
    })

    # Moderately similar
    hist_strikes3 = np.linspace(400, 500, 100)
    hist_pdf3 = norm.pdf(hist_strikes3, loc=449, scale=16)
    historical_data.append({
        'date': '2023-11-05',
        'pdf': hist_pdf3,
        'strikes': hist_strikes3,
        'stats': {
            'skewness': -0.18,
            'excess_kurtosis': 0.6,
            'implied_move_pct': 3.5
        }
    })

    # Find matches
    matcher = PDFPatternMatcher(similarity_threshold=0.70, max_matches=3)

    matches = matcher.find_similar_patterns(
        current_pdf=current_pdf,
        current_strikes=current_strikes,
        current_stats=current_stats,
        historical_data=historical_data
    )

    # Print results
    print("="*60)
    print("PATTERN MATCHING RESULTS")
    print("="*60)
    print(f"Found {len(matches)} similar patterns:\n")

    for i, match in enumerate(matches, 1):
        print(f"{i}. {match['date']}")
        print(f"   Similarity: {match['similarity']:.2%}")
        print(f"   Description: {match['description']}")
        print(f"   Stats: Skew={match['stats']['skewness']:.2f}, "
              f"Kurt={match['stats']['excess_kurtosis']:.2f}, "
              f"Move={match['stats']['implied_move_pct']:.1f}%")
        print()

    print("="*60)

    # Validate results
    assert len(matches) > 0, "Should find at least one match"
    assert matches[0]['similarity'] > 0.85, "First match should be very similar"
    assert matches[0]['date'] == '2023-10-15', "Most similar should be the first historical entry"

    print("✅ PDF Pattern Matcher test passed!")
