"""
Helper functions for Streamlit app.
"""

import streamlit as st
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


def load_custom_css():
    """Load custom CSS styling for the app (Dark Theme Optimized)."""
    st.markdown("""
    <style>
    /* Main title styling */
    h1 {
        color: #4dabf7;
        padding-bottom: 10px;
        border-bottom: 2px solid #4dabf7;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
        color: #fafafa;
    }

    /* Sidebar styling - Dark Theme */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }

    /* Info boxes - Dark Theme */
    .info-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e3a5f;
        border-left: 5px solid #4dabf7;
        margin: 10px 0;
        color: #e8e8e8;
    }

    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e3d2f;
        border-left: 5px solid #51cf66;
        margin: 10px 0;
        color: #e8e8e8;
    }

    .warning-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #3d3416;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
        color: #e8e8e8;
    }

    .error-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #3d1e1e;
        border-left: 5px solid #ff6b6b;
        margin: 10px 0;
        color: #e8e8e8;
    }

    /* Code blocks - Dark Theme */
    code {
        background-color: #2d2d2d;
        color: #f8f8f2;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }

    /* Tables - Dark Theme */
    table {
        width: 100%;
        border-collapse: collapse;
        color: #fafafa;
    }

    th {
        background-color: #1f77b4;
        color: white;
        padding: 12px;
        text-align: left;
    }

    td {
        padding: 10px;
        border-bottom: 1px solid #444;
        color: #e8e8e8;
    }

    tr:hover {
        background-color: #2a2a2a;
    }

    /* Additional dark theme enhancements */
    .stMarkdown {
        color: #fafafa;
    }

    p {
        color: #e8e8e8;
    }

    /* Ensure all text is visible */
    * {
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with commas and decimals."""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage."""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def format_date(dt: datetime) -> str:
    """Format datetime for display."""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M")


def format_date_short(dt: datetime) -> str:
    """Format datetime (date only)."""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d")


def show_success(message: str):
    """Display success message."""
    st.markdown(f"""
    <div class="success-box">
        <strong>✅ Success!</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def show_info(message: str):
    """Display info message."""
    st.markdown(f"""
    <div class="info-box">
        <strong>ℹ️ Info</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def show_warning(message: str):
    """Display warning message."""
    st.markdown(f"""
    <div class="warning-box">
        <strong>⚠️ Warning</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def show_error(message: str):
    """Display error message."""
    st.markdown(f"""
    <div class="error-box">
        <strong>❌ Error</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def get_expiration_date(days_from_now: int) -> datetime:
    """Calculate expiration date from days."""
    return datetime.now() + timedelta(days=days_from_now)


def calculate_days_to_expiry(expiration_date: datetime) -> int:
    """Calculate days to expiration from date."""
    delta = expiration_date - datetime.now()
    return max(0, delta.days)


def format_statistics_table(stats: Dict[str, Any]) -> str:
    """
    Format statistics as HTML table.

    Args:
        stats: Statistics dictionary

    Returns:
        HTML table string
    """
    rows = []

    # Basic stats
    if 'mean' in stats:
        rows.append(f"<tr><td>Expected Price (Mean)</td><td>${format_number(stats['mean'])}</td></tr>")

    if 'std' in stats:
        rows.append(f"<tr><td>Volatility (Std Dev)</td><td>${format_number(stats['std'])}</td></tr>")

    if 'implied_move_pct' in stats:
        rows.append(f"<tr><td>Implied Move</td><td>±{format_percentage(stats['implied_move_pct']/100)}</td></tr>")

    # Shape stats
    if 'skewness' in stats:
        skew_direction = "Bearish" if stats['skewness'] < 0 else "Bullish"
        rows.append(f"<tr><td>Skewness</td><td>{format_number(stats['skewness'], 3)} ({skew_direction})</td></tr>")

    if 'excess_kurtosis' in stats:
        rows.append(f"<tr><td>Excess Kurtosis</td><td>{format_number(stats['excess_kurtosis'], 3)}</td></tr>")

    # Tail probabilities
    if 'prob_up_5pct' in stats:
        rows.append(f"<tr><td>Prob(+5% move)</td><td>{format_percentage(stats['prob_up_5pct'])}</td></tr>")

    if 'prob_down_5pct' in stats:
        rows.append(f"<tr><td>Prob(-5% move)</td><td>{format_percentage(stats['prob_down_5pct'])}</td></tr>")

    if 'prob_up_10pct' in stats:
        rows.append(f"<tr><td>Prob(+10% move)</td><td>{format_percentage(stats['prob_up_10pct'])}</td></tr>")

    if 'prob_down_10pct' in stats:
        rows.append(f"<tr><td>Prob(-10% move)</td><td>{format_percentage(stats['prob_down_10pct'])}</td></tr>")

    # Confidence intervals
    if 'ci_68_lower' in stats and 'ci_68_upper' in stats:
        rows.append(f"<tr><td>68% CI</td><td>${format_number(stats['ci_68_lower'])} - ${format_number(stats['ci_68_upper'])}</td></tr>")

    if 'ci_95_lower' in stats and 'ci_95_upper' in stats:
        rows.append(f"<tr><td>95% CI</td><td>${format_number(stats['ci_95_lower'])} - ${format_number(stats['ci_95_upper'])}</td></tr>")

    table_html = f"""
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """

    return table_html


def create_download_link(data: Any, filename: str, link_text: str = "Download") -> str:
    """
    Create download link for data.

    Args:
        data: Data to download (will be JSON stringified)
        filename: Name of file to download
        link_text: Text for download link

    Returns:
        HTML download link
    """
    import json
    import base64

    json_str = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()

    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">{link_text}</a>'
    return href


def calculate_price_range(spot: float, pct: float = 0.2) -> tuple:
    """
    Calculate price range around spot.

    Args:
        spot: Spot price
        pct: Percentage range (default 20%)

    Returns:
        (min_price, max_price)
    """
    min_price = spot * (1 - pct)
    max_price = spot * (1 + pct)
    return min_price, max_price


def get_color_for_probability(prob: float) -> str:
    """
    Get color for probability value.

    Args:
        prob: Probability (0-1)

    Returns:
        Color string
    """
    if prob < 0.05:
        return "#f8d7da"  # Light red
    elif prob < 0.15:
        return "#fff3cd"  # Light yellow
    elif prob < 0.25:
        return "#d1ecf1"  # Light blue
    else:
        return "#d4edda"  # Light green


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if text is None:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def validate_ticker(ticker: str) -> bool:
    """Validate ticker symbol."""
    if not ticker:
        return False
    # Basic validation: 1-5 uppercase letters
    return ticker.isalpha() and ticker.isupper() and 1 <= len(ticker) <= 5


def get_analysis_mode_description(mode: str) -> str:
    """Get description for analysis mode."""
    descriptions = {
        'standard': 'Balanced analysis suitable for most users',
        'conservative': 'Focus on risk and downside scenarios',
        'aggressive': 'Focus on opportunities and upside potential',
        'educational': 'Detailed explanations with learning focus'
    }
    return descriptions.get(mode, 'Unknown mode')
