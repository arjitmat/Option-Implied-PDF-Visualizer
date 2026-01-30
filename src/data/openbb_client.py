"""
OpenBB client for fetching SPY/SPX option chain data.
This is the primary data source for option prices.
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from openbb import obb


class OpenBBClient:
    """Client for fetching option data from OpenBB."""

    def __init__(self):
        """Initialize OpenBB client."""
        # OpenBB 4.0+ doesn't require explicit initialization
        pass

    def get_spy_options(
        self,
        ticker: str = "SPY",
        min_expiry_days: int = 7,
        max_expiry_days: int = 90
    ) -> pd.DataFrame:
        """
        Fetch SPY option chain data.

        Args:
            ticker: Ticker symbol (SPY or SPX)
            min_expiry_days: Minimum days to expiration
            max_expiry_days: Maximum days to expiration

        Returns:
            DataFrame with columns:
                - strike: Strike price
                - expiration: Expiration date
                - optionType: 'call' or 'put'
                - bid: Bid price
                - ask: Ask price
                - lastPrice: Last traded price
                - volume: Volume
                - openInterest: Open interest
                - impliedVolatility: Implied volatility
                - delta: Option delta
                - gamma: Option gamma
                - theta: Option theta
                - vega: Option vega
        """
        try:
            # Fetch option chain using OpenBB 4.0+ API
            data = obb.equity.options.chains(
                symbol=ticker,
                provider="intrinio"  # Free provider
            )

            if data is None or len(data) == 0:
                raise ValueError(f"No option data returned for {ticker}")

            # Convert to DataFrame
            df = data.to_df()

            # Filter by expiration date
            today = pd.Timestamp.now()
            df['days_to_expiry'] = (pd.to_datetime(df['expiration']) - today).dt.days

            df = df[
                (df['days_to_expiry'] >= min_expiry_days) &
                (df['days_to_expiry'] <= max_expiry_days)
            ]

            # Clean data
            df = self._clean_option_data(df)

            return df

        except Exception as e:
            raise RuntimeError(f"Failed to fetch option data from OpenBB: {str(e)}")

    def get_spot_price(self, ticker: str = "SPY") -> float:
        """
        Get current spot price for the underlying.

        Args:
            ticker: Ticker symbol

        Returns:
            Current price
        """
        try:
            quote = obb.equity.quote(symbol=ticker)
            df = quote.to_df()
            return float(df['last_price'].iloc[0])
        except Exception as e:
            raise RuntimeError(f"Failed to fetch spot price: {str(e)}")

    def get_option_expirations(self, ticker: str = "SPY") -> List[str]:
        """
        Get available option expiration dates.

        Args:
            ticker: Ticker symbol

        Returns:
            List of expiration dates (YYYY-MM-DD format)
        """
        try:
            df = self.get_spy_options(ticker=ticker, min_expiry_days=0, max_expiry_days=365)
            expirations = df['expiration'].unique()
            return sorted([str(d) for d in expirations])
        except Exception as e:
            raise RuntimeError(f"Failed to fetch expirations: {str(e)}")

    def get_options_by_expiration(
        self,
        expiration_date: str,
        ticker: str = "SPY"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get calls and puts for a specific expiration date.

        Args:
            expiration_date: Expiration date (YYYY-MM-DD)
            ticker: Ticker symbol

        Returns:
            Tuple of (calls_df, puts_df)
        """
        df = self.get_spy_options(ticker=ticker, min_expiry_days=0, max_expiry_days=365)
        df_exp = df[df['expiration'] == expiration_date]

        calls = df_exp[df_exp['optionType'] == 'call'].sort_values('strike')
        puts = df_exp[df_exp['optionType'] == 'put'].sort_values('strike')

        return calls, puts

    def _clean_option_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate option data.

        Args:
            df: Raw option DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Remove rows with missing critical data
        df = df.dropna(subset=['strike', 'lastPrice', 'impliedVolatility'])

        # Remove zero or negative prices
        df = df[df['lastPrice'] > 0]

        # Remove zero or negative IV
        df = df[df['impliedVolatility'] > 0]

        # Calculate mid price from bid-ask if available
        if 'bid' in df.columns and 'ask' in df.columns:
            df['midPrice'] = (df['bid'] + df['ask']) / 2
            # Use mid price if available and reasonable
            df['price'] = df.apply(
                lambda row: row['midPrice']
                if pd.notna(row['midPrice']) and row['midPrice'] > 0
                else row['lastPrice'],
                axis=1
            )
        else:
            df['price'] = df['lastPrice']

        # Sort by strike
        df = df.sort_values(['expiration', 'strike'])

        return df


def get_spy_options(*args, **kwargs) -> pd.DataFrame:
    """Convenience function to fetch SPY options."""
    client = OpenBBClient()
    return client.get_spy_options(*args, **kwargs)


def get_spot_price(ticker: str = "SPY") -> float:
    """Convenience function to get spot price."""
    client = OpenBBClient()
    return client.get_spot_price(ticker)


if __name__ == "__main__":
    # Test the client
    print("Testing OpenBB client...")

    try:
        client = OpenBBClient()

        # Get spot price
        spot = client.get_spot_price("SPY")
        print(f"SPY spot price: ${spot:.2f}")

        # Get option chain
        options = client.get_spy_options("SPY", min_expiry_days=20, max_expiry_days=40)
        print(f"\nFetched {len(options)} option contracts")
        print(f"Expirations: {options['expiration'].unique()}")
        print(f"Strike range: ${options['strike'].min():.2f} - ${options['strike'].max():.2f}")

        # Show sample data
        print("\nSample data:")
        print(options.head())

        print("\n✅ OpenBB client test passed!")

    except Exception as e:
        print(f"\n❌ OpenBB client test failed: {str(e)}")
