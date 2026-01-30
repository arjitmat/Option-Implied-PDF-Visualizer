"""
Breeden-Litzenberger formula for extracting risk-neutral probability density
from option prices.

The key insight: The second derivative of call option prices with respect to
strike gives the risk-neutral probability density function.

Formula: f(K) = e^(rT) × ∂²C/∂K²
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
from scipy import interpolate
try:
    from scipy.integrate import trapezoid, cumulative_trapezoid
except ImportError:
    # Fallback for older scipy versions
    from scipy.integrate import trapz as trapezoid, cumtrapz as cumulative_trapezoid

from src.core.sabr import calibrate_volatility_surface
from config.constants import (
    MIN_STRIKES_FOR_PDF,
    PDF_GRID_POINTS,
    MIN_STRIKE_PCT,
    MAX_STRIKE_PCT
)


class BreedenlitzenbergPDF:
    """
    Calculate probability density function from option prices using
    the Breeden-Litzenberger formula.
    """

    def __init__(self):
        """Initialize PDF calculator."""
        self.pdf = None
        self.strikes = None
        self.cdf = None
        self.spot = None
        self.params = {}

    def calculate_from_options(
        self,
        options_df: pd.DataFrame,
        spot_price: float,
        risk_free_rate: float,
        time_to_expiry: float,
        option_type: str = 'call',
        interpolation_method: str = 'sabr'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate PDF from option market data.

        Args:
            options_df: DataFrame with columns ['strike', 'price', 'impliedVolatility']
            spot_price: Current spot price
            risk_free_rate: Risk-free rate (as decimal)
            time_to_expiry: Time to expiration in years
            option_type: 'call' or 'put'
            interpolation_method: 'sabr' or 'spline'

        Returns:
            Tuple of (strikes, pdf_values)
        """
        self.spot = spot_price
        self.params = {
            'risk_free_rate': risk_free_rate,
            'time_to_expiry': time_to_expiry,
            'option_type': option_type
        }

        # Filter to reasonable strike range
        min_strike = spot_price * MIN_STRIKE_PCT
        max_strike = spot_price * MAX_STRIKE_PCT

        df = options_df[
            (options_df['strike'] >= min_strike) &
            (options_df['strike'] <= max_strike) &
            (options_df['price'] > 0)
        ].copy()

        if len(df) < MIN_STRIKES_FOR_PDF:
            raise ValueError(
                f"Need at least {MIN_STRIKES_FOR_PDF} strikes, got {len(df)}"
            )

        # Sort by strike
        df = df.sort_values('strike')

        # Use mid price if available
        if 'price' not in df.columns and 'bid' in df.columns and 'ask' in df.columns:
            df['price'] = (df['bid'] + df['ask']) / 2

        market_strikes = df['strike'].values
        market_prices = df['price'].values
        market_ivs = df['impliedVolatility'].values

        # Step 1: Interpolate volatility surface
        forward = spot_price * np.exp(risk_free_rate * time_to_expiry)

        vol_model, vol_stats = calibrate_volatility_surface(
            market_strikes,
            market_ivs,
            forward,
            time_to_expiry,
            method=interpolation_method
        )

        # Step 2: Create fine grid of strikes
        strike_grid = np.linspace(min_strike, max_strike, PDF_GRID_POINTS)

        # Step 3: Get interpolated implied volatilities
        interp_ivs = vol_model.get_volatility(strike_grid)

        # Step 4: Calculate option prices on fine grid using Black-Scholes
        if option_type == 'call':
            interp_prices = self._black_scholes_call(
                strike_grid, spot_price, risk_free_rate, time_to_expiry, interp_ivs
            )
        else:
            interp_prices = self._black_scholes_put(
                strike_grid, spot_price, risk_free_rate, time_to_expiry, interp_ivs
            )

        # Step 5: Apply Breeden-Litzenberger formula
        pdf = self._breeden_litzenberger(
            strike_grid, interp_prices, risk_free_rate, time_to_expiry
        )

        # Step 6: Normalize PDF (should integrate to 1)
        pdf = self._normalize_pdf(strike_grid, pdf)

        # Store results
        self.strikes = strike_grid
        self.pdf = pdf

        # Calculate CDF
        self.cdf = self._calculate_cdf(strike_grid, pdf)

        return strike_grid, pdf

    def _breeden_litzenberger(
        self,
        strikes: np.ndarray,
        call_prices: np.ndarray,
        r: float,
        T: float
    ) -> np.ndarray:
        """
        Apply Breeden-Litzenberger formula: f(K) = e^(rT) × ∂²C/∂K²

        Args:
            strikes: Strike prices
            call_prices: Call option prices
            r: Risk-free rate
            T: Time to expiration

        Returns:
            Probability density values
        """
        # Calculate strike spacing
        dK = np.gradient(strikes)

        # First derivative: ∂C/∂K
        dC_dK = np.gradient(call_prices, strikes)

        # Second derivative: ∂²C/∂K²
        d2C_dK2 = np.gradient(dC_dK, strikes)

        # Apply formula
        pdf = np.exp(r * T) * d2C_dK2

        # Ensure non-negative (numerical issues can cause small negative values)
        pdf = np.maximum(pdf, 0)

        # Smooth out numerical noise
        from scipy.signal import savgol_filter
        try:
            window_length = min(51, len(pdf) if len(pdf) % 2 == 1 else len(pdf) - 1)
            if window_length >= 5:
                pdf = savgol_filter(pdf, window_length=window_length, polyorder=3)
                pdf = np.maximum(pdf, 0)  # Ensure still non-negative after smoothing
        except:
            pass  # Skip smoothing if it fails

        return pdf

    def _normalize_pdf(self, strikes: np.ndarray, pdf: np.ndarray) -> np.ndarray:
        """
        Normalize PDF so it integrates to 1.

        Args:
            strikes: Strike prices
            pdf: PDF values

        Returns:
            Normalized PDF
        """
        integral = trapezoid(pdf, strikes)

        if integral <= 0:
            raise ValueError("PDF integral is zero or negative - invalid PDF")

        return pdf / integral

    def _calculate_cdf(self, strikes: np.ndarray, pdf: np.ndarray) -> np.ndarray:
        """
        Calculate cumulative distribution function.

        Args:
            strikes: Strike prices
            pdf: PDF values

        Returns:
            CDF values
        """
        cdf = cumulative_trapezoid(pdf, strikes, initial=0)

        # Ensure CDF ends at 1.0
        cdf = cdf / cdf[-1] if cdf[-1] > 0 else cdf

        return cdf

    def _black_scholes_call(
        self,
        K: np.ndarray,
        S: float,
        r: float,
        T: float,
        sigma: np.ndarray
    ) -> np.ndarray:
        """Calculate Black-Scholes call price."""
        from scipy.stats import norm

        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

        return call_price

    def _black_scholes_put(
        self,
        K: np.ndarray,
        S: float,
        r: float,
        T: float,
        sigma: np.ndarray
    ) -> np.ndarray:
        """Calculate Black-Scholes put price."""
        from scipy.stats import norm

        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return put_price

    def get_probability(self, strike_level: float, condition: str = 'below') -> float:
        """
        Get probability of spot being above/below a strike level.

        Args:
            strike_level: Strike price
            condition: 'below' or 'above'

        Returns:
            Probability (0 to 1)
        """
        if self.cdf is None or self.strikes is None:
            raise ValueError("PDF must be calculated first")

        # Interpolate CDF to get probability at exact strike
        cdf_interp = interpolate.interp1d(
            self.strikes, self.cdf, kind='linear', fill_value='extrapolate'
        )

        prob_below = float(cdf_interp(strike_level))

        if condition == 'below':
            return prob_below
        elif condition == 'above':
            return 1 - prob_below
        else:
            raise ValueError("condition must be 'below' or 'above'")

    def get_probability_range(
        self,
        lower_strike: float,
        upper_strike: float
    ) -> float:
        """
        Get probability of spot being within a strike range.

        Args:
            lower_strike: Lower strike
            upper_strike: Upper strike

        Returns:
            Probability
        """
        prob_below_upper = self.get_probability(upper_strike, 'below')
        prob_below_lower = self.get_probability(lower_strike, 'below')

        return prob_below_upper - prob_below_lower


def calculate_pdf_from_options(
    options_df: pd.DataFrame,
    spot_price: float,
    risk_free_rate: float,
    time_to_expiry: float,
    **kwargs
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to calculate PDF.

    Args:
        options_df: Options data
        spot_price: Spot price
        risk_free_rate: Risk-free rate
        time_to_expiry: Time to expiry in years
        **kwargs: Additional arguments for BreedenlitzenbergPDF

    Returns:
        Tuple of (strikes, pdf)
    """
    calculator = BreedenlitzenbergPDF()
    return calculator.calculate_from_options(
        options_df, spot_price, risk_free_rate, time_to_expiry, **kwargs
    )


if __name__ == "__main__":
    # Test with synthetic data
    print("Testing Breeden-Litzenberger PDF calculation...")

    # Create synthetic option chain
    spot = 450.0
    r = 0.05
    T = 30 / 365
    atm_vol = 0.20

    strikes = np.linspace(400, 500, 50)

    # Generate implied vols with smile
    ivs = atm_vol * (1 + 0.0005 * (strikes - spot)**2 / spot**2)

    # Calculate BS prices
    from scipy.stats import norm
    d1 = (np.log(spot / strikes) + (r + 0.5 * ivs**2) * T) / (ivs * np.sqrt(T))
    d2 = d1 - ivs * np.sqrt(T)
    call_prices = spot * norm.cdf(d1) - strikes * np.exp(-r * T) * norm.cdf(d2)

    # Create DataFrame
    options_df = pd.DataFrame({
        'strike': strikes,
        'price': call_prices,
        'impliedVolatility': ivs
    })

    # Calculate PDF
    calculator = BreedenlitzenbergPDF()
    pdf_strikes, pdf_values = calculator.calculate_from_options(
        options_df, spot, r, T, option_type='call'
    )

    # Validate
    integral = trapezoid(pdf_values, pdf_strikes)
    print(f"\nPDF integral: {integral:.6f} (should be ~1.0)")

    # Check statistics
    mean = trapezoid(pdf_strikes * pdf_values, pdf_strikes)
    variance = trapezoid((pdf_strikes - mean)**2 * pdf_values, pdf_strikes)
    std = np.sqrt(variance)

    print(f"Expected spot (mean): ${mean:.2f} (actual: ${spot:.2f})")
    print(f"Standard deviation: ${std:.2f}")

    # Probability calculations
    prob_below_450 = calculator.get_probability(450, 'below')
    prob_above_450 = calculator.get_probability(450, 'above')
    prob_range_440_460 = calculator.get_probability_range(440, 460)

    print(f"\nProbabilities:")
    print(f"  P(S < $450): {prob_below_450:.2%}")
    print(f"  P(S > $450): {prob_above_450:.2%}")
    print(f"  P($440 < S < $460): {prob_range_440_460:.2%}")

    assert 0.99 < integral < 1.01, f"PDF should integrate to 1, got {integral}"

    print("\n✅ Breeden-Litzenberger test passed!")
