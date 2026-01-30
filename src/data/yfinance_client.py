"""
YFinance client for fetching SPY/SPX option chain data.
This is a backup data source when OpenBB is unavailable.
"""

from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf


class YFinanceClient:
    """Client for fetching option data from Yahoo Finance."""

    def __init__(self):
        """Initialize YFinance client."""
        pass

    def get_spy_options(
        self,
        ticker: str = "SPY",
        min_expiry_days: int = 7,
        max_expiry_days: int = 90
    ) -> pd.DataFrame:
        """
        Fetch SPY option chain data from Yahoo Finance.

        Args:
            ticker: Ticker symbol (SPY or ^SPX)
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
        """
        try:
            # Create ticker object
            stock = yf.Ticker(ticker)

            # Get all expiration dates
            expirations = stock.options

            if not expirations:
                raise ValueError(f"No option data available for {ticker}")

            # Filter expirations by date range
            today = datetime.now()
            valid_expirations = []

            for exp_str in expirations:
                exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
                days_to_exp = (exp_date - today).days

                if min_expiry_days <= days_to_exp <= max_expiry_days:
                    valid_expirations.append(exp_str)

            if not valid_expirations:
                raise ValueError(
                    f"No expirations found between {min_expiry_days} and {max_expiry_days} days"
                )

            # Fetch option chains for valid expirations
            all_options = []

            for exp_date in valid_expirations:
                try:
                    # Get option chain
                    opt_chain = stock.option_chain(exp_date)

                    # Process calls
                    calls = opt_chain.calls.copy()
                    calls['optionType'] = 'call'
                    calls['expiration'] = exp_date

                    # Process puts
                    puts = opt_chain.puts.copy()
                    puts['optionType'] = 'put'
                    puts['expiration'] = exp_date

                    # Combine
                    all_options.extend([calls, puts])

                except Exception as e:
                    print(f"Warning: Failed to fetch options for {exp_date}: {str(e)}")
                    continue

            if not all_options:
                raise ValueError("Failed to fetch any option data")

            # Concatenate all data
            df = pd.concat(all_options, ignore_index=True)

            # Standardize column names
            df = self._standardize_columns(df)

            # Calculate days to expiry
            df['days_to_expiry'] = df['expiration'].apply(
                lambda x: (datetime.strptime(x, '%Y-%m-%d') - today).days
            )

            # Clean data
            df = self._clean_option_data(df)

            return df

        except Exception as e:
            raise RuntimeError(f"Failed to fetch option data from YFinance: {str(e)}")

    def get_spot_price(self, ticker: str = "SPY") -> float:
        """
        Get current spot price for the underlying.

        Args:
            ticker: Ticker symbol

        Returns:
            Current price
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return float(info.get('currentPrice', info.get('regularMarketPrice', 0)))
        except Exception as e:
            # Fallback: get from recent history
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')
                return float(hist['Close'].iloc[-1])
            except:
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
            stock = yf.Ticker(ticker)
            return list(stock.options)
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
        try:
            stock = yf.Ticker(ticker)
            opt_chain = stock.option_chain(expiration_date)

            calls = opt_chain.calls.copy()
            calls = self._standardize_columns(calls)
            calls['expiration'] = expiration_date
            calls['optionType'] = 'call'

            puts = opt_chain.puts.copy()
            puts = self._standardize_columns(puts)
            puts['expiration'] = expiration_date
            puts['optionType'] = 'put'

            return calls, puts

        except Exception as e:
            raise RuntimeError(f"Failed to fetch options for {expiration_date}: {str(e)}")

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to match OpenBB format.

        Args:
            df: Raw yfinance DataFrame

        Returns:
            DataFrame with standardized columns
        """
        # YFinance uses different column names
        column_mapping = {
            'strike': 'strike',
            'lastPrice': 'lastPrice',
            'bid': 'bid',
            'ask': 'ask',
            'volume': 'volume',
            'openInterest': 'openInterest',
            'impliedVolatility': 'impliedVolatility'
        }

        # Rename columns if they exist
        df = df.rename(columns=column_mapping)

        return df

    def _clean_option_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate option data.

        Args:
            df: Raw option DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Remove rows with missing critical data
        df = df.dropna(subset=['strike', 'lastPrice'])

        # Remove zero or negative prices
        df = df[df['lastPrice'] > 0]

        # For IV, be more lenient - fill with reasonable defaults if missing
        if 'impliedVolatility' not in df.columns:
            df['impliedVolatility'] = 0.20  # Default 20% IV
        else:
            # Fill missing IVs with mean of available IVs
            df['impliedVolatility'] = df['impliedVolatility'].fillna(df['impliedVolatility'].mean())
            # Remove rows with still invalid IVs
            df = df[df['impliedVolatility'] > 0]
            df = df[df['impliedVolatility'] < 5.0]  # Remove unrealistic IVs > 500%

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
    client = YFinanceClient()
    return client.get_spy_options(*args, **kwargs)


def get_spot_price(ticker: str = "SPY") -> float:
    """Convenience function to get spot price."""
    client = YFinanceClient()
    return client.get_spot_price(ticker)


if __name__ == "__main__":
    # Test the client
    print("Testing YFinance client...")

    try:
        client = YFinanceClient()

        # Get spot price
        spot = client.get_spot_price("SPY")
        print(f"SPY spot price: ${spot:.2f}")

        # Get available expirations
        expirations = client.get_option_expirations("SPY")
        print(f"\nAvailable expirations: {expirations[:5]}")

        # Get option chain
        options = client.get_spy_options("SPY", min_expiry_days=20, max_expiry_days=40)
        print(f"\nFetched {len(options)} option contracts")
        print(f"Expirations: {options['expiration'].unique()}")
        print(f"Strike range: ${options['strike'].min():.2f} - ${options['strike'].max():.2f}")

        # Show sample data
        print("\nSample data:")
        print(options[['strike', 'expiration', 'optionType', 'lastPrice', 'impliedVolatility']].head())

        print("\n✅ YFinance client test passed!")

    except Exception as e:
        print(f"\n❌ YFinance client test failed: {str(e)}")
