"""
Unified data manager with automatic fallback between data sources.
"""

from typing import Optional, Tuple, List
import pandas as pd
from datetime import datetime

from src.data.openbb_client import OpenBBClient
from src.data.yfinance_client import YFinanceClient
from src.data.fred_client import FREDClient
from src.data.cache import DataCache
from config.settings import DATA_SOURCE_PRIORITY, CACHE_TTL_MINUTES
from config.constants import MIN_EXPIRY_DAYS, MAX_EXPIRY_DAYS


class DataManager:
    """
    Unified data manager with intelligent fallback and caching.

    Features:
    - Automatic fallback between data sources
    - Built-in caching for performance
    - Unified API across different providers
    """

    def __init__(
        self,
        use_cache: bool = True,
        cache_ttl_minutes: int = CACHE_TTL_MINUTES
    ):
        """
        Initialize data manager.

        Args:
            use_cache: Whether to use caching
            cache_ttl_minutes: Cache time-to-live in minutes
        """
        # Initialize clients
        self.openbb_client = OpenBBClient()
        self.yfinance_client = YFinanceClient()
        self.fred_client = FREDClient()

        # Initialize cache
        self.use_cache = use_cache
        self.cache = DataCache(ttl_minutes=cache_ttl_minutes) if use_cache else None

        # Track which data source is currently working
        self.active_source = None

    def get_options(
        self,
        ticker: str = "SPY",
        min_expiry_days: int = MIN_EXPIRY_DAYS,
        max_expiry_days: int = MAX_EXPIRY_DAYS,
        force_source: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get option chain data with automatic fallback.

        Args:
            ticker: Ticker symbol
            min_expiry_days: Minimum days to expiration
            max_expiry_days: Maximum days to expiration
            force_source: Force specific data source ('openbb' or 'yfinance')

        Returns:
            DataFrame with option data
        """
        # Check cache first
        cache_key = f"options_{ticker}_{min_expiry_days}_{max_expiry_days}"
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # Determine data sources to try
        if force_source:
            sources = [force_source]
        else:
            sources = DATA_SOURCE_PRIORITY.copy()

        # Try each data source in priority order
        last_error = None
        for source in sources:
            try:
                if source == 'openbb':
                    data = self.openbb_client.get_spy_options(
                        ticker=ticker,
                        min_expiry_days=min_expiry_days,
                        max_expiry_days=max_expiry_days
                    )
                elif source == 'yfinance':
                    data = self.yfinance_client.get_spy_options(
                        ticker=ticker,
                        min_expiry_days=min_expiry_days,
                        max_expiry_days=max_expiry_days
                    )
                else:
                    continue

                # Success! Cache and return
                self.active_source = source
                if self.use_cache:
                    self.cache.set(cache_key, data)
                return data

            except Exception as e:
                last_error = e
                print(f"Warning: {source} failed: {str(e)}")
                continue

        # All sources failed
        raise RuntimeError(
            f"All data sources failed to fetch options for {ticker}. "
            f"Last error: {str(last_error)}"
        )

    def get_spot_price(
        self,
        ticker: str = "SPY",
        force_source: Optional[str] = None
    ) -> float:
        """
        Get current spot price with automatic fallback.

        Args:
            ticker: Ticker symbol
            force_source: Force specific data source

        Returns:
            Current spot price
        """
        # Check cache
        cache_key = f"spot_{ticker}"
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # Determine sources
        sources = [force_source] if force_source else DATA_SOURCE_PRIORITY.copy()

        # Try each source
        last_error = None
        for source in sources:
            try:
                if source == 'openbb':
                    price = self.openbb_client.get_spot_price(ticker)
                elif source == 'yfinance':
                    price = self.yfinance_client.get_spot_price(ticker)
                else:
                    continue

                # Cache and return
                if self.use_cache:
                    self.cache.set(cache_key, price)
                return price

            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"Failed to fetch spot price for {ticker}. Last error: {str(last_error)}"
        )

    def get_risk_free_rate(
        self,
        days_to_maturity: Optional[int] = None
    ) -> float:
        """
        Get risk-free interest rate.

        Args:
            days_to_maturity: Optional maturity in days

        Returns:
            Risk-free rate as decimal
        """
        # Check cache
        cache_key = f"rfr_{days_to_maturity or 'default'}"
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # Fetch from FRED with fallback
        try:
            if days_to_maturity:
                rate = self.fred_client.get_rate_for_maturity(days_to_maturity)
            else:
                rate = self.fred_client.get_risk_free_rate()
        except Exception as e:
            # Fallback to default rate if FRED client fails entirely
            print(f"Warning: FRED client failed ({str(e)}), using default rate of 4.5%")
            rate = 0.045

        # Cache and return
        if self.use_cache:
            self.cache.set(cache_key, rate)
        return rate

    def get_options_by_expiration(
        self,
        expiration_date: str,
        ticker: str = "SPY",
        force_source: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get calls and puts for specific expiration.

        Args:
            expiration_date: Expiration date (YYYY-MM-DD)
            ticker: Ticker symbol
            force_source: Force specific data source

        Returns:
            Tuple of (calls_df, puts_df)
        """
        # Check cache
        cache_key = f"options_exp_{ticker}_{expiration_date}"
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # Determine sources
        sources = [force_source] if force_source else DATA_SOURCE_PRIORITY.copy()

        # Try each source
        last_error = None
        for source in sources:
            try:
                if source == 'openbb':
                    calls, puts = self.openbb_client.get_options_by_expiration(
                        expiration_date, ticker
                    )
                elif source == 'yfinance':
                    calls, puts = self.yfinance_client.get_options_by_expiration(
                        expiration_date, ticker
                    )
                else:
                    continue

                # Cache and return
                result = (calls, puts)
                if self.use_cache:
                    self.cache.set(cache_key, result)
                return result

            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"Failed to fetch options for {expiration_date}. Last error: {str(last_error)}"
        )

    def get_expirations(
        self,
        ticker: str = "SPY",
        force_source: Optional[str] = None
    ) -> List[str]:
        """
        Get available expiration dates.

        Args:
            ticker: Ticker symbol
            force_source: Force specific data source

        Returns:
            List of expiration dates
        """
        # Check cache
        cache_key = f"expirations_{ticker}"
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # Determine sources
        sources = [force_source] if force_source else DATA_SOURCE_PRIORITY.copy()

        # Try each source
        last_error = None
        for source in sources:
            try:
                if source == 'openbb':
                    expirations = self.openbb_client.get_option_expirations(ticker)
                elif source == 'yfinance':
                    expirations = self.yfinance_client.get_option_expirations(ticker)
                else:
                    continue

                # Cache and return
                if self.use_cache:
                    self.cache.set(cache_key, expirations)
                return expirations

            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"Failed to fetch expirations for {ticker}. Last error: {str(last_error)}"
        )

    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear cache."""
        if self.cache:
            self.cache.clear(key)

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        if self.cache:
            return self.cache.get_cache_stats()
        return {}


# Create global instance
_global_manager = None


def get_data_manager() -> DataManager:
    """Get global data manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = DataManager()
    return _global_manager


if __name__ == "__main__":
    # Test the data manager
    print("Testing DataManager...")

    try:
        manager = DataManager()

        # Test spot price
        spot = manager.get_spot_price("SPY")
        print(f"SPY spot price: ${spot:.2f}")

        # Test risk-free rate
        rfr = manager.get_risk_free_rate(30)
        print(f"30-day risk-free rate: {rfr:.4f} ({rfr*100:.2f}%)")

        # Test option chain
        options = manager.get_options("SPY", min_expiry_days=20, max_expiry_days=40)
        print(f"\nFetched {len(options)} option contracts")
        print(f"Data source used: {manager.active_source}")
        print(f"Expirations: {options['expiration'].unique()}")

        # Test cache stats
        print(f"\nCache stats: {manager.get_cache_stats()}")

        print("\n✅ DataManager test passed!")

    except Exception as e:
        print(f"\n❌ DataManager test failed: {str(e)}")
