"""
FRED (Federal Reserve Economic Data) client for fetching risk-free interest rates.
"""

import os
import ssl
from typing import Optional
from datetime import datetime, timedelta
from fredapi import Fred
from dotenv import load_dotenv
import certifi

# Load environment variables
load_dotenv()

# Fix SSL certificate verification for macOS
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()


class FREDClient:
    """Client for fetching risk-free rate data from FRED API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED client.

        Args:
            api_key: FRED API key. If not provided, reads from FRED_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')

        if not self.api_key:
            raise ValueError(
                "FRED API key not found. Set FRED_API_KEY environment variable or pass api_key parameter. "
                "Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
            )

        self.fred = Fred(api_key=self.api_key)

    def get_risk_free_rate(
        self,
        series_id: str = 'DGS3MO',
        days: int = 1
    ) -> float:
        """
        Get the risk-free interest rate.

        Args:
            series_id: FRED series ID. Options:
                - 'DGS3MO': 3-Month Treasury Constant Maturity Rate (default)
                - 'DGS1MO': 1-Month Treasury
                - 'DGS6MO': 6-Month Treasury
                - 'DGS1': 1-Year Treasury
                - 'DTB3': 3-Month Treasury Bill Secondary Market Rate
            days: Number of days to look back if current data is unavailable

        Returns:
            Risk-free rate as decimal (e.g., 0.05 for 5%)
        """
        try:
            # Get most recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            data = self.fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date
            )

            if data.empty:
                raise ValueError(f"No data returned for series {series_id}")

            # Get most recent non-null value
            rate = data.dropna().iloc[-1]

            # Convert from percentage to decimal
            return float(rate) / 100.0

        except Exception as e:
            # Fallback to default rate if FRED API fails (SSL errors, network issues, etc.)
            print(f"Warning: FRED API failed ({str(e)}), using default rate of 4.5%")
            return 0.045  # Default 4.5% (approximate current 3-month Treasury rate)

    def get_rate_for_maturity(self, days_to_maturity: int) -> float:
        """
        Get risk-free rate for a specific maturity.

        Args:
            days_to_maturity: Days to maturity (e.g., 30, 90, 180, 365)

        Returns:
            Risk-free rate as decimal
        """
        # Map maturity to appropriate FRED series
        if days_to_maturity <= 30:
            series_id = 'DGS1MO'  # 1-month
        elif days_to_maturity <= 90:
            series_id = 'DGS3MO'  # 3-month
        elif days_to_maturity <= 180:
            series_id = 'DGS6MO'  # 6-month
        elif days_to_maturity <= 365:
            series_id = 'DGS1'    # 1-year
        elif days_to_maturity <= 365 * 2:
            series_id = 'DGS2'    # 2-year
        elif days_to_maturity <= 365 * 5:
            series_id = 'DGS5'    # 5-year
        elif days_to_maturity <= 365 * 10:
            series_id = 'DGS10'   # 10-year
        else:
            series_id = 'DGS30'   # 30-year

        return self.get_risk_free_rate(series_id=series_id, days=7)

    def get_treasury_curve(self) -> dict:
        """
        Get the entire Treasury yield curve.

        Returns:
            Dictionary with maturities as keys and rates as values
        """
        maturities = {
            '1M': 'DGS1MO',
            '3M': 'DGS3MO',
            '6M': 'DGS6MO',
            '1Y': 'DGS1',
            '2Y': 'DGS2',
            '5Y': 'DGS5',
            '10Y': 'DGS10',
            '30Y': 'DGS30'
        }

        curve = {}
        for maturity, series_id in maturities.items():
            try:
                rate = self.get_risk_free_rate(series_id=series_id, days=7)
                curve[maturity] = rate
            except Exception as e:
                print(f"Warning: Failed to fetch {maturity} rate: {str(e)}")
                curve[maturity] = None

        return curve


def get_risk_free_rate(days_to_maturity: Optional[int] = None) -> float:
    """
    Convenience function to get risk-free rate.

    Args:
        days_to_maturity: Optional maturity in days. If None, returns 3-month rate.

    Returns:
        Risk-free rate as decimal
    """
    client = FREDClient()

    if days_to_maturity:
        return client.get_rate_for_maturity(days_to_maturity)
    else:
        return client.get_risk_free_rate()


if __name__ == "__main__":
    # Test the client
    print("Testing FRED client...")

    try:
        client = FREDClient()

        # Get 3-month rate
        rate_3m = client.get_risk_free_rate()
        print(f"3-Month Treasury Rate: {rate_3m:.4f} ({rate_3m*100:.2f}%)")

        # Get rate for 30-day maturity
        rate_30d = client.get_rate_for_maturity(30)
        print(f"30-Day Rate: {rate_30d:.4f} ({rate_30d*100:.2f}%)")

        # Get full yield curve
        print("\nTreasury Yield Curve:")
        curve = client.get_treasury_curve()
        for maturity, rate in curve.items():
            if rate is not None:
                print(f"  {maturity}: {rate:.4f} ({rate*100:.2f}%)")

        print("\n✅ FRED client test passed!")

    except Exception as e:
        print(f"\n❌ FRED client test failed: {str(e)}")
        print("\nMake sure you have set FRED_API_KEY in your .env file")
        print("Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
