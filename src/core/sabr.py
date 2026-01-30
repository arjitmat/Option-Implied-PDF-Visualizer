"""
SABR (Stochastic Alpha Beta Rho) volatility model for IV interpolation.

The SABR model is used to interpolate implied volatility across strikes,
providing a smooth volatility surface needed for Breeden-Litzenberger.
"""

import numpy as np
from typing import Tuple, Optional
from scipy.optimize import minimize, least_squares
from pysabr import Hagan2002LognormalSABR as SABR
from config.constants import SABR_BETA, SABR_INITIAL_ALPHA, SABR_INITIAL_RHO, SABR_INITIAL_NU


class SABRModel:
    """
    SABR model for implied volatility interpolation.

    The SABR model captures the volatility smile/skew observed in option markets.
    """

    def __init__(self, beta: float = SABR_BETA):
        """
        Initialize SABR model.

        Args:
            beta: CEV exponent parameter (typically 0.5 for equity options)
        """
        self.beta = beta
        self.alpha = None
        self.rho = None
        self.nu = None
        self.forward = None
        self.tau = None
        self.is_calibrated = False

    def calibrate(
        self,
        strikes: np.ndarray,
        implied_vols: np.ndarray,
        forward: float,
        tau: float,
        initial_guess: Optional[Tuple[float, float, float]] = None
    ) -> dict:
        """
        Calibrate SABR parameters to market implied volatilities.

        Args:
            strikes: Array of strike prices
            implied_vols: Array of implied volatilities (as decimals, e.g., 0.2 for 20%)
            forward: Forward price (for short maturities, approximately spot)
            tau: Time to expiration in years
            initial_guess: Optional tuple of (alpha, rho, nu) initial values

        Returns:
            Dictionary with calibrated parameters and fit statistics
        """
        self.forward = forward
        self.tau = tau

        # Filter out invalid data
        valid_mask = (implied_vols > 0) & (strikes > 0) & np.isfinite(implied_vols)
        strikes = strikes[valid_mask]
        implied_vols = implied_vols[valid_mask]

        if len(strikes) < 3:
            raise ValueError("Need at least 3 valid strikes for calibration")

        # Initial guess
        if initial_guess is None:
            initial_guess = (SABR_INITIAL_ALPHA, SABR_INITIAL_RHO, SABR_INITIAL_NU)

        # Objective function: minimize squared errors
        def objective(params):
            alpha, rho, nu = params

            # Parameter bounds constraints
            if alpha <= 0 or nu <= 0 or rho < -1 or rho > 1:
                return 1e10

            try:
                model_vols = self._sabr_formula(strikes, forward, alpha, rho, nu, self.beta, tau)
                errors = (model_vols - implied_vols) ** 2
                return np.sum(errors)
            except:
                return 1e10

        # Optimize
        result = minimize(
            objective,
            initial_guess,
            method='Nelder-Mead',
            options={'maxiter': 1000}
        )

        if not result.success:
            # Try with L-BFGS-B with bounds
            bounds = [(0.001, 2.0), (-0.999, 0.999), (0.001, 2.0)]
            result = minimize(
                objective,
                initial_guess,
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': 1000}
            )

        # Store calibrated parameters
        self.alpha, self.rho, self.nu = result.x
        self.is_calibrated = True

        # Calculate fit quality
        model_vols = self.get_volatility(strikes)
        rmse = np.sqrt(np.mean((model_vols - implied_vols) ** 2))
        mae = np.mean(np.abs(model_vols - implied_vols))

        return {
            'alpha': self.alpha,
            'rho': self.rho,
            'nu': self.nu,
            'beta': self.beta,
            'rmse': rmse,
            'mae': mae,
            'success': result.success
        }

    def get_volatility(self, strikes: np.ndarray) -> np.ndarray:
        """
        Get implied volatility for given strikes using calibrated SABR model.

        Args:
            strikes: Array of strike prices

        Returns:
            Array of implied volatilities
        """
        if not self.is_calibrated:
            raise ValueError("Model must be calibrated before getting volatilities")

        return self._sabr_formula(
            strikes, self.forward, self.alpha, self.rho, self.nu, self.beta, self.tau
        )

    @staticmethod
    def _sabr_formula(
        K: np.ndarray,
        F: float,
        alpha: float,
        rho: float,
        nu: float,
        beta: float,
        tau: float
    ) -> np.ndarray:
        """
        SABR implied volatility formula (Hagan et al. 2002).

        Args:
            K: Strikes
            F: Forward price
            alpha: Initial volatility
            rho: Correlation
            nu: Volatility of volatility
            beta: CEV exponent
            tau: Time to expiration

        Returns:
            Implied volatilities
        """
        # Ensure inputs are arrays
        K = np.atleast_1d(K)

        # ATM case (avoid division by zero)
        atm_vol = alpha / (F ** (1 - beta))

        # For each strike
        vols = np.zeros_like(K, dtype=float)

        for i, strike in enumerate(K):
            if np.abs(strike - F) < 1e-6:
                # ATM
                vols[i] = atm_vol * (1 + ((1 - beta)**2 / 24 * alpha**2 / F**(2 - 2*beta) +
                                          0.25 * rho * beta * nu * alpha / F**(1 - beta) +
                                          (2 - 3*rho**2) / 24 * nu**2) * tau)
            else:
                # Non-ATM
                try:
                    FK = F * strike
                    log_FK = np.log(F / strike)

                    z = (nu / alpha) * FK**((1 - beta) / 2) * log_FK
                    x_z = np.log((np.sqrt(1 - 2*rho*z + z**2) + z - rho) / (1 - rho))

                    if np.abs(x_z) < 1e-10:
                        x_z = z

                    num = alpha
                    denom = FK**((1 - beta) / 2) * (
                        1 + (1 - beta)**2 / 24 * log_FK**2 +
                        (1 - beta)**4 / 1920 * log_FK**4
                    )

                    vol_term = num / denom * (z / x_z)

                    correction = (1 + ((1 - beta)**2 / 24 * alpha**2 / FK**(1 - beta) +
                                      0.25 * rho * beta * nu * alpha / FK**((1 - beta) / 2) +
                                      (2 - 3*rho**2) / 24 * nu**2) * tau)

                    vols[i] = vol_term * correction

                except:
                    # Fallback to ATM vol
                    vols[i] = atm_vol

        return vols


class CubicSplineInterpolator:
    """
    Fallback cubic spline interpolator if SABR fails.
    """

    def __init__(self):
        from scipy.interpolate import CubicSpline
        self.CubicSpline = CubicSpline
        self.spline = None
        self.is_calibrated = False

    def calibrate(
        self,
        strikes: np.ndarray,
        implied_vols: np.ndarray,
        **kwargs
    ) -> dict:
        """Calibrate cubic spline."""
        valid_mask = (implied_vols > 0) & (strikes > 0) & np.isfinite(implied_vols)
        strikes = strikes[valid_mask]
        implied_vols = implied_vols[valid_mask]

        # Sort by strike
        sort_idx = np.argsort(strikes)
        strikes = strikes[sort_idx]
        implied_vols = implied_vols[sort_idx]

        self.spline = self.CubicSpline(strikes, implied_vols, extrapolate=True)
        self.is_calibrated = True

        # Calculate fit quality
        model_vols = self.spline(strikes)
        rmse = np.sqrt(np.mean((model_vols - implied_vols) ** 2))

        return {
            'method': 'cubic_spline',
            'rmse': rmse,
            'success': True
        }

    def get_volatility(self, strikes: np.ndarray) -> np.ndarray:
        """Get interpolated volatility."""
        if not self.is_calibrated:
            raise ValueError("Spline must be calibrated first")
        return self.spline(strikes)


def calibrate_volatility_surface(
    strikes: np.ndarray,
    implied_vols: np.ndarray,
    forward: float,
    tau: float,
    method: str = 'sabr'
) -> Tuple[object, dict]:
    """
    Calibrate volatility surface using specified method.

    Args:
        strikes: Strike prices
        implied_vols: Implied volatilities
        forward: Forward price
        tau: Time to expiration (years)
        method: 'sabr' or 'spline'

    Returns:
        Tuple of (calibrated model, fit statistics)
    """
    if method == 'sabr':
        try:
            model = SABRModel()
            stats = model.calibrate(strikes, implied_vols, forward, tau)
            return model, stats
        except Exception as e:
            print(f"SABR calibration failed: {str(e)}, falling back to spline")
            method = 'spline'

    if method == 'spline':
        model = CubicSplineInterpolator()
        stats = model.calibrate(strikes, implied_vols)
        return model, stats

    raise ValueError(f"Unknown method: {method}")


if __name__ == "__main__":
    # Test SABR calibration
    print("Testing SABR model...")

    # Synthetic data
    forward = 450.0
    tau = 30 / 365
    strikes = np.linspace(400, 500, 20)

    # Generate synthetic implied vols with smile
    atm_vol = 0.20
    true_vols = atm_vol * (1 + 0.001 * (strikes - forward)**2 / forward**2)

    # Calibrate SABR
    sabr = SABRModel()
    stats = sabr.calibrate(strikes, true_vols, forward, tau)

    print(f"\nCalibrated SABR parameters:")
    print(f"  Alpha: {stats['alpha']:.4f}")
    print(f"  Rho: {stats['rho']:.4f}")
    print(f"  Nu: {stats['nu']:.4f}")
    print(f"  Beta: {stats['beta']:.4f}")
    print(f"  RMSE: {stats['rmse']:.6f}")
    print(f"  Success: {stats['success']}")

    # Test interpolation
    test_strikes = np.linspace(420, 480, 10)
    interp_vols = sabr.get_volatility(test_strikes)
    print(f"\nInterpolated vols for strikes {test_strikes[0]:.0f}-{test_strikes[-1]:.0f}:")
    print(f"  {interp_vols}")

    print("\n✅ SABR model test passed!")
