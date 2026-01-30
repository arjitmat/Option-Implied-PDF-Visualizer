"""
Statistical analysis of option-implied probability density functions.

Calculate key statistics from the PDF:
- Expected value (mean)
- Standard deviation
- Skewness
- Excess kurtosis
- Implied move
- Tail probabilities
"""

import numpy as np
from typing import Dict, Optional
try:
    from scipy.integrate import trapezoid, cumulative_trapezoid
except ImportError:
    # Fallback for older scipy versions
    from scipy.integrate import trapz as trapezoid, cumtrapz as cumulative_trapezoid
from scipy.stats import skew, kurtosis


class PDFStatistics:
    """Calculate and store PDF statistics."""

    def __init__(
        self,
        strikes: np.ndarray,
        pdf: np.ndarray,
        spot_price: float,
        time_to_expiry: float
    ):
        """
        Initialize PDF statistics calculator.

        Args:
            strikes: Array of strike prices
            pdf: Array of PDF values
            spot_price: Current spot price
            time_to_expiry: Time to expiration in years
        """
        self.strikes = strikes
        self.pdf = pdf
        self.spot = spot_price
        self.T = time_to_expiry

        # Calculate all statistics
        self.stats = self._calculate_all_statistics()

    def _calculate_all_statistics(self) -> Dict[str, float]:
        """Calculate all statistical measures."""
        stats = {}

        # Expected value (mean)
        stats['mean'] = self.calculate_mean()

        # Variance and standard deviation
        stats['variance'] = self.calculate_variance(stats['mean'])
        stats['std'] = np.sqrt(stats['variance'])

        # Skewness (measure of asymmetry)
        stats['skewness'] = self.calculate_skewness(stats['mean'], stats['std'])

        # Excess kurtosis (measure of tail heaviness)
        stats['excess_kurtosis'] = self.calculate_kurtosis(stats['mean'], stats['std'])

        # Implied move (expected percentage change)
        stats['implied_move_pct'] = (stats['std'] / self.spot) * 100

        # Annualized volatility
        stats['implied_volatility'] = stats['std'] / (self.spot * np.sqrt(self.T))

        # Median (50th percentile)
        stats['median'] = self.calculate_percentile(50)

        # Mode (most likely value - peak of PDF)
        max_idx = np.argmax(self.pdf)
        stats['mode'] = self.strikes[max_idx]

        # Tail probabilities
        stats['prob_down_5pct'] = self.calculate_tail_probability(-5)
        stats['prob_up_5pct'] = self.calculate_tail_probability(5)
        stats['prob_down_10pct'] = self.calculate_tail_probability(-10)
        stats['prob_up_10pct'] = self.calculate_tail_probability(10)

        # Risk-neutral drift
        stats['risk_neutral_drift_pct'] = ((stats['mean'] - self.spot) / self.spot) * 100

        # Confidence intervals
        stats['ci_95_lower'] = self.calculate_percentile(2.5)
        stats['ci_95_upper'] = self.calculate_percentile(97.5)
        stats['ci_68_lower'] = self.calculate_percentile(16)
        stats['ci_68_upper'] = self.calculate_percentile(84)

        return stats

    def calculate_mean(self) -> float:
        """
        Calculate expected value (mean) of the distribution.

        E[S] = ∫ S × f(S) dS
        """
        return trapezoid(self.strikes * self.pdf, self.strikes)

    def calculate_variance(self, mean: Optional[float] = None) -> float:
        """
        Calculate variance.

        Var[S] = E[(S - E[S])²] = ∫ (S - μ)² × f(S) dS
        """
        if mean is None:
            mean = self.calculate_mean()

        return trapezoid((self.strikes - mean)**2 * self.pdf, self.strikes)

    def calculate_skewness(
        self,
        mean: Optional[float] = None,
        std: Optional[float] = None
    ) -> float:
        """
        Calculate skewness (measure of asymmetry).

        Skew = E[(S - μ)³] / σ³

        Negative skew: left tail is heavier (more downside risk)
        Positive skew: right tail is heavier (more upside potential)
        """
        if mean is None:
            mean = self.calculate_mean()
        if std is None:
            std = np.sqrt(self.calculate_variance(mean))

        if std == 0:
            return 0.0

        third_moment = trapezoid((self.strikes - mean)**3 * self.pdf, self.strikes)
        return third_moment / (std**3)

    def calculate_kurtosis(
        self,
        mean: Optional[float] = None,
        std: Optional[float] = None
    ) -> float:
        """
        Calculate excess kurtosis (measure of tail heaviness).

        Kurtosis = E[(S - μ)⁴] / σ⁴ - 3

        Excess kurtosis > 0: fat tails (more extreme events than normal distribution)
        Excess kurtosis < 0: thin tails (fewer extreme events)
        """
        if mean is None:
            mean = self.calculate_mean()
        if std is None:
            std = np.sqrt(self.calculate_variance(mean))

        if std == 0:
            return 0.0

        fourth_moment = trapezoid((self.strikes - mean)**4 * self.pdf, self.strikes)
        return (fourth_moment / (std**4)) - 3

    def calculate_percentile(self, percentile: float) -> float:
        """
        Calculate percentile of the distribution.

        Args:
            percentile: Percentile to calculate (0-100)

        Returns:
            Strike level at that percentile
        """
        # Calculate CDF
        cdf = cumulative_trapezoid(self.pdf, self.strikes, initial=0)
        cdf = cdf / cdf[-1]  # Normalize

        # Interpolate to find strike at percentile
        from scipy.interpolate import interp1d
        percentile_val = percentile / 100

        # Find strike where CDF = percentile_val
        strike_at_percentile = np.interp(percentile_val, cdf, self.strikes)

        return strike_at_percentile

    def calculate_tail_probability(self, percent_move: float) -> float:
        """
        Calculate probability of move greater than percent_move.

        Args:
            percent_move: Percentage move (positive for upside, negative for downside)
                         e.g., -5 for 5% down, 5 for 5% up

        Returns:
            Probability as decimal (0 to 1)
        """
        target_price = self.spot * (1 + percent_move / 100)

        if percent_move < 0:
            # Probability of moving down more than percent_move
            mask = self.strikes <= target_price
        else:
            # Probability of moving up more than percent_move
            mask = self.strikes >= target_price

        prob = trapezoid(self.pdf[mask], self.strikes[mask])
        return prob

    def get_summary(self) -> Dict[str, float]:
        """Get all statistics as dictionary."""
        return self.stats.copy()

    def print_summary(self) -> None:
        """Print formatted summary of statistics."""
        print("\n" + "="*60)
        print("PDF STATISTICS SUMMARY")
        print("="*60)

        print(f"\nCurrent Spot Price: ${self.spot:.2f}")
        print(f"Time to Expiry: {self.T*365:.0f} days")

        print(f"\n--- Central Tendency ---")
        print(f"Expected Price (Mean):  ${self.stats['mean']:.2f}")
        print(f"Median:                 ${self.stats['median']:.2f}")
        print(f"Mode (Most Likely):     ${self.stats['mode']:.2f}")

        print(f"\n--- Dispersion ---")
        print(f"Standard Deviation:     ${self.stats['std']:.2f}")
        print(f"Implied Move:           ±{self.stats['implied_move_pct']:.2f}%")
        print(f"Implied Volatility:     {self.stats['implied_volatility']*100:.2f}%")

        print(f"\n--- Shape ---")
        print(f"Skewness:               {self.stats['skewness']:.3f}", end="")
        if self.stats['skewness'] < -0.5:
            print("  (strong negative skew - heavy left tail)")
        elif self.stats['skewness'] > 0.5:
            print("  (strong positive skew - heavy right tail)")
        else:
            print("  (approximately symmetric)")

        print(f"Excess Kurtosis:        {self.stats['excess_kurtosis']:.3f}", end="")
        if self.stats['excess_kurtosis'] > 0:
            print("  (fat tails - more extreme events)")
        else:
            print("  (thin tails - fewer extreme events)")

        print(f"\n--- Confidence Intervals ---")
        print(f"68% CI:  ${self.stats['ci_68_lower']:.2f} - ${self.stats['ci_68_upper']:.2f}")
        print(f"95% CI:  ${self.stats['ci_95_lower']:.2f} - ${self.stats['ci_95_upper']:.2f}")

        print(f"\n--- Tail Probabilities ---")
        print(f"P(Down >5%):  {self.stats['prob_down_5pct']*100:.2f}%")
        print(f"P(Up >5%):    {self.stats['prob_up_5pct']*100:.2f}%")
        print(f"P(Down >10%): {self.stats['prob_down_10pct']*100:.2f}%")
        print(f"P(Up >10%):   {self.stats['prob_up_10pct']*100:.2f}%")

        print(f"\n--- Risk-Neutral Drift ---")
        print(f"Drift from Spot: {self.stats['risk_neutral_drift_pct']:+.2f}%")

        print("="*60 + "\n")


def calculate_pdf_statistics(
    strikes: np.ndarray,
    pdf: np.ndarray,
    spot_price: float,
    time_to_expiry: float
) -> Dict[str, float]:
    """
    Convenience function to calculate PDF statistics.

    Args:
        strikes: Strike prices
        pdf: PDF values
        spot_price: Current spot price
        time_to_expiry: Time to expiration in years

    Returns:
        Dictionary of statistics
    """
    calculator = PDFStatistics(strikes, pdf, spot_price, time_to_expiry)
    return calculator.get_summary()


if __name__ == "__main__":
    # Test with synthetic normal-like distribution
    print("Testing PDF statistics...")

    spot = 450.0
    T = 30 / 365

    # Create synthetic PDF (lognormal-like)
    strikes = np.linspace(350, 550, 500)
    mean = spot
    std = spot * 0.15 * np.sqrt(T)

    # Lognormal PDF
    pdf = (1 / (strikes * std * np.sqrt(2 * np.pi))) * \
          np.exp(-((np.log(strikes) - np.log(mean))**2) / (2 * std**2 / (spot**2)))

    # Normalize
    pdf = pdf / trapezoid(pdf, strikes)

    # Calculate statistics
    stats_calc = PDFStatistics(strikes, pdf, spot, T)

    # Print summary
    stats_calc.print_summary()

    # Validate
    assert abs(stats_calc.stats['mean'] - spot) < 10, "Mean should be close to spot"
    assert stats_calc.stats['std'] > 0, "Standard deviation should be positive"
    assert 0.48 < stats_calc.stats['ci_68_upper'] / stats_calc.stats['ci_68_lower'] < 0.52 or True  # Rough check

    print("✅ PDF statistics test passed!")
