"""
Probability table components for displaying probability data in structured format.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional
from src.visualization.themes import DARK_THEME


def create_probability_table(
    probabilities: Dict[str, float],
    spot_price: float,
    title: str = "Probability Analysis"
) -> go.Figure:
    """
    Create formatted table of probabilities.

    Args:
        probabilities: Dictionary of probability labels and values
        spot_price: Current spot price
        title: Table title

    Returns:
        Plotly table figure
    """
    # Prepare data
    labels = []
    values = []
    colors = []

    for label, prob in probabilities.items():
        labels.append(label)
        values.append(f"{prob*100:.2f}%")

        # Color code by probability level
        if prob > 0.3:
            colors.append('rgba(0, 255, 136, 0.3)')  # Green for high prob
        elif prob > 0.15:
            colors.append('rgba(255, 215, 0, 0.3)')  # Yellow for medium prob
        else:
            colors.append('rgba(255, 68, 68, 0.3)')  # Red for low prob

    # Create table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Scenario</b>', '<b>Probability</b>'],
            fill_color=DARK_THEME['plot_bg'],
            align='left',
            font=dict(color=DARK_THEME['text'], size=14),
            height=40
        ),
        cells=dict(
            values=[labels, values],
            fill_color=[colors, colors],
            align='left',
            font=dict(color=DARK_THEME['text'], size=12),
            height=30
        )
    )])

    fig.update_layout(
        title=title,
        paper_bgcolor=DARK_THEME['background'],
        font=dict(color=DARK_THEME['text']),
        height=min(400, 100 + len(labels) * 35),
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def create_strikes_table(
    strikes: np.ndarray,
    probabilities: np.ndarray,
    spot_price: float,
    num_strikes: int = 10,
    title: str = "Strike Probabilities"
) -> go.Figure:
    """
    Create table showing probabilities at specific strike levels.

    Args:
        strikes: Strike prices
        probabilities: Probability values (CDF - cumulative)
        spot_price: Current spot price
        num_strikes: Number of strikes to display
        title: Table title

    Returns:
        Plotly table figure
    """
    # Select strikes around spot price
    spot_idx = np.argmin(np.abs(strikes - spot_price))

    # Get range of strikes
    start_idx = max(0, spot_idx - num_strikes // 2)
    end_idx = min(len(strikes), start_idx + num_strikes)
    start_idx = max(0, end_idx - num_strikes)  # Adjust if at end

    selected_strikes = strikes[start_idx:end_idx]
    selected_probs = probabilities[start_idx:end_idx]

    # Create data
    strike_labels = [f"${s:.2f}" for s in selected_strikes]
    prob_below = [f"{p*100:.2f}%" for p in selected_probs]
    prob_above = [f"{(1-p)*100:.2f}%" for p in selected_probs]

    # Color code strikes relative to spot
    colors = []
    for strike in selected_strikes:
        if abs(strike - spot_price) < spot_price * 0.01:  # Within 1% of spot
            colors.append('rgba(0, 255, 136, 0.3)')  # Green for ATM
        elif strike < spot_price:
            colors.append('rgba(0, 217, 255, 0.2)')  # Cyan for ITM
        else:
            colors.append('rgba(255, 0, 255, 0.2)')  # Magenta for OTM

    # Create table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Strike</b>', '<b>P(S < K)</b>', '<b>P(S > K)</b>'],
            fill_color=DARK_THEME['plot_bg'],
            align='center',
            font=dict(color=DARK_THEME['text'], size=14),
            height=40
        ),
        cells=dict(
            values=[strike_labels, prob_below, prob_above],
            fill_color=[colors, colors, colors],
            align='center',
            font=dict(color=DARK_THEME['text'], size=12),
            height=30
        )
    )])

    fig.update_layout(
        title=title,
        paper_bgcolor=DARK_THEME['background'],
        font=dict(color=DARK_THEME['text']),
        height=min(500, 100 + num_strikes * 35),
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def create_statistics_table(
    stats: Dict[str, float],
    spot_price: float,
    title: str = "PDF Statistics"
) -> go.Figure:
    """
    Create formatted table of PDF statistics.

    Args:
        stats: Dictionary of statistics from PDFStatistics
        spot_price: Current spot price
        title: Table title

    Returns:
        Plotly table figure
    """
    # Organize statistics into categories
    categories = []
    metrics = []
    values = []

    # Central Tendency
    categories.extend(['Central Tendency'] * 3)
    metrics.extend(['Expected Price (Mean)', 'Median', 'Mode'])
    values.extend([
        f"${stats['mean']:.2f}",
        f"${stats['median']:.2f}",
        f"${stats['mode']:.2f}"
    ])

    # Dispersion
    categories.extend(['Dispersion'] * 3)
    metrics.extend(['Standard Deviation', 'Implied Move', 'Implied Volatility'])
    values.extend([
        f"${stats['std']:.2f}",
        f"±{stats['implied_move_pct']:.2f}%",
        f"{stats['implied_volatility']*100:.2f}%"
    ])

    # Shape
    categories.extend(['Shape'] * 2)
    metrics.extend(['Skewness', 'Excess Kurtosis'])
    values.extend([
        f"{stats['skewness']:.3f}",
        f"{stats['excess_kurtosis']:.3f}"
    ])

    # Tail Probabilities
    categories.extend(['Tail Risk'] * 4)
    metrics.extend(['P(Down >5%)', 'P(Up >5%)', 'P(Down >10%)', 'P(Up >10%)'])
    values.extend([
        f"{stats['prob_down_5pct']*100:.2f}%",
        f"{stats['prob_up_5pct']*100:.2f}%",
        f"{stats['prob_down_10pct']*100:.2f}%",
        f"{stats['prob_up_10pct']*100:.2f}%"
    ])

    # Confidence Intervals
    categories.extend(['Confidence Intervals'] * 2)
    metrics.extend(['68% CI', '95% CI'])
    values.extend([
        f"${stats['ci_68_lower']:.2f} - ${stats['ci_68_upper']:.2f}",
        f"${stats['ci_95_lower']:.2f} - ${stats['ci_95_upper']:.2f}"
    ])

    # Current Price
    categories.append('Reference')
    metrics.append('Current Spot Price')
    values.append(f"${spot_price:.2f}")

    # Color code by category
    category_colors = {
        'Central Tendency': 'rgba(0, 217, 255, 0.2)',
        'Dispersion': 'rgba(0, 255, 136, 0.2)',
        'Shape': 'rgba(255, 215, 0, 0.2)',
        'Tail Risk': 'rgba(255, 68, 68, 0.2)',
        'Confidence Intervals': 'rgba(255, 0, 255, 0.2)',
        'Reference': 'rgba(150, 150, 150, 0.2)'
    }

    colors = [category_colors[cat] for cat in categories]

    # Create table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Category</b>', '<b>Metric</b>', '<b>Value</b>'],
            fill_color=DARK_THEME['plot_bg'],
            align='left',
            font=dict(color=DARK_THEME['text'], size=14),
            height=40
        ),
        cells=dict(
            values=[categories, metrics, values],
            fill_color=[colors, colors, colors],
            align=['left', 'left', 'right'],
            font=dict(color=DARK_THEME['text'], size=12),
            height=30
        )
    )])

    fig.update_layout(
        title=title,
        paper_bgcolor=DARK_THEME['background'],
        font=dict(color=DARK_THEME['text']),
        height=min(800, 100 + len(categories) * 30),
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def create_comparison_table(
    comparison_data: Dict[str, Dict[str, float]],
    title: str = "Multi-Expiration Comparison"
) -> go.Figure:
    """
    Create comparison table across multiple expirations.

    Args:
        comparison_data: Dictionary with format:
            {
                'expiration_label': {
                    'mean': float,
                    'std': float,
                    'skewness': float,
                    ...
                }
            }
        title: Table title

    Returns:
        Plotly table figure
    """
    if not comparison_data:
        raise ValueError("No data provided for comparison")

    # Get all expirations
    expirations = list(comparison_data.keys())

    # Metrics to compare
    metrics = ['mean', 'std', 'implied_move_pct', 'skewness', 'excess_kurtosis']
    metric_labels = ['Mean ($)', 'Std Dev ($)', 'Implied Move (%)', 'Skewness', 'Kurtosis']

    # Build table data
    table_data = [metric_labels]

    for exp in expirations:
        data = comparison_data[exp]
        row = []
        for metric in metrics:
            value = data.get(metric, 0)
            if metric in ['mean', 'std']:
                row.append(f"${value:.2f}")
            elif metric == 'implied_move_pct':
                row.append(f"±{value:.2f}%")
            else:
                row.append(f"{value:.3f}")
        table_data.append(row)

    # Create table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Metric</b>'] + [f'<b>{exp}</b>' for exp in expirations],
            fill_color=DARK_THEME['plot_bg'],
            align='center',
            font=dict(color=DARK_THEME['text'], size=14),
            height=40
        ),
        cells=dict(
            values=table_data,
            fill_color=DARK_THEME['background'],
            align='center',
            font=dict(color=DARK_THEME['text'], size=12),
            height=30
        )
    )])

    fig.update_layout(
        title=title,
        paper_bgcolor=DARK_THEME['background'],
        font=dict(color=DARK_THEME['text']),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


if __name__ == "__main__":
    # Test probability tables
    print("Testing probability tables...")

    spot = 450.0

    # Test 1: Simple probability table
    probabilities = {
        'P(Price < $440)': 0.25,
        'P($440 < Price < $450)': 0.25,
        'P($450 < Price < $460)': 0.30,
        'P(Price > $460)': 0.20
    }

    fig1 = create_probability_table(probabilities, spot)
    fig1.write_html("test_prob_table.html")
    print("✅ Probability table saved to test_prob_table.html")

    # Test 2: Strikes table
    strikes = np.linspace(430, 470, 20)
    cdf = np.linspace(0.1, 0.9, 20)  # Synthetic CDF

    fig2 = create_strikes_table(strikes, cdf, spot, num_strikes=10)
    fig2.write_html("test_strikes_table.html")
    print("✅ Strikes table saved to test_strikes_table.html")

    # Test 3: Statistics table
    stats = {
        'mean': 451.5,
        'median': 450.8,
        'mode': 450.0,
        'std': 15.2,
        'implied_move_pct': 3.38,
        'implied_volatility': 0.20,
        'skewness': -0.15,
        'excess_kurtosis': 0.5,
        'prob_down_5pct': 0.18,
        'prob_up_5pct': 0.22,
        'prob_down_10pct': 0.08,
        'prob_up_10pct': 0.10,
        'ci_68_lower': 436.3,
        'ci_68_upper': 466.7,
        'ci_95_lower': 421.1,
        'ci_95_upper': 481.9
    }

    fig3 = create_statistics_table(stats, spot)
    fig3.write_html("test_stats_table.html")
    print("✅ Statistics table saved to test_stats_table.html")

    # Test 4: Comparison table
    comparison = {
        '15D': {
            'mean': 450.5,
            'std': 10.2,
            'implied_move_pct': 2.27,
            'skewness': -0.10,
            'excess_kurtosis': 0.3
        },
        '30D': {
            'mean': 451.2,
            'std': 15.0,
            'implied_move_pct': 3.33,
            'skewness': -0.15,
            'excess_kurtosis': 0.5
        },
        '60D': {
            'mean': 452.0,
            'std': 22.5,
            'implied_move_pct': 4.98,
            'skewness': -0.20,
            'excess_kurtosis': 0.7
        }
    }

    fig4 = create_comparison_table(comparison)
    fig4.write_html("test_comparison_table.html")
    print("✅ Comparison table saved to test_comparison_table.html")

    print("\n✅ All probability table tests passed!")
