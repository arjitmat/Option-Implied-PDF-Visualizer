"""
2D PDF visualization components.

Create single and comparison plots for probability density functions.
"""

import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
from src.visualization.themes import (
    create_base_layout,
    get_line_style,
    format_hover_template,
    DARK_THEME
)


def plot_pdf_2d(
    strikes: np.ndarray,
    pdf: np.ndarray,
    spot_price: float,
    title: str = "Option-Implied Probability Density",
    show_spot: bool = True,
    show_ci: bool = True,
    ci_levels: Tuple[float, float] = (0.16, 0.84)
) -> go.Figure:
    """
    Create 2D plot of probability density function.

    Args:
        strikes: Strike prices
        pdf: PDF values
        spot_price: Current spot price
        title: Plot title
        show_spot: Whether to show vertical line at spot price
        show_ci: Whether to show confidence interval shading
        ci_levels: Confidence interval levels (default: 68% CI)

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Main PDF line
    fig.add_trace(go.Scatter(
        x=strikes,
        y=pdf,
        mode='lines',
        name='PDF',
        line=dict(
            color=DARK_THEME['primary'],
            width=3
        ),
        fill='tozeroy',
        fillcolor=f"rgba(0, 217, 255, 0.2)",  # Semi-transparent cyan
        hovertemplate=format_hover_template("Strike", "Probability Density")
    ))

    # Add spot price indicator
    if show_spot:
        fig.add_vline(
            x=spot_price,
            line_dash="dash",
            line_color=DARK_THEME['success'],
            line_width=2,
            annotation_text=f"Spot: ${spot_price:.2f}",
            annotation_position="top"
        )

    # Add confidence interval shading
    if show_ci and ci_levels:
        try:
            from scipy.integrate import cumulative_trapezoid
        except ImportError:
            from scipy.integrate import cumtrapz as cumulative_trapezoid

        # Calculate CDF
        cdf = cumulative_trapezoid(pdf, strikes, initial=0)
        cdf = cdf / cdf[-1]  # Normalize

        # Find strikes at CI levels
        lower_strike = np.interp(ci_levels[0], cdf, strikes)
        upper_strike = np.interp(ci_levels[1], cdf, strikes)

        # Add shaded region
        ci_mask = (strikes >= lower_strike) & (strikes <= upper_strike)

        fig.add_trace(go.Scatter(
            x=strikes[ci_mask],
            y=pdf[ci_mask],
            mode='lines',
            name=f'{int((ci_levels[1]-ci_levels[0])*100)}% CI',
            line=dict(width=0),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 136, 0.15)',  # Semi-transparent green
            showlegend=True,
            hoverinfo='skip'
        ))

        # Add vertical lines for CI bounds
        fig.add_vline(
            x=lower_strike,
            line_dash="dot",
            line_color=DARK_THEME['neutral'],
            line_width=1,
            annotation_text=f"${lower_strike:.2f}",
            annotation_position="bottom"
        )
        fig.add_vline(
            x=upper_strike,
            line_dash="dot",
            line_color=DARK_THEME['neutral'],
            line_width=1,
            annotation_text=f"${upper_strike:.2f}",
            annotation_position="bottom"
        )

    # Layout
    layout = create_base_layout(
        title=title,
        xaxis_title="Strike Price ($)",
        yaxis_title="Probability Density",
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(20,20,20,0.8)',
            bordercolor=DARK_THEME['grid'],
            borderwidth=1
        )
    )

    fig.update_layout(**layout)

    return fig


def plot_pdf_comparison(
    pdf_data: Dict[str, Dict[str, np.ndarray]],
    spot_price: float,
    title: str = "PDF Comparison Across Expirations"
) -> go.Figure:
    """
    Create comparison plot of multiple PDFs.

    Args:
        pdf_data: Dictionary with format:
            {
                'expiration_date': {
                    'strikes': np.ndarray,
                    'pdf': np.ndarray,
                    'days_to_expiry': int
                }
            }
        spot_price: Current spot price
        title: Plot title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Sort by days to expiry
    sorted_data = sorted(
        pdf_data.items(),
        key=lambda x: x[1]['days_to_expiry']
    )

    # Add each PDF as a line
    for idx, (exp_date, data) in enumerate(sorted_data):
        strikes = data['strikes']
        pdf = data['pdf']
        days = data['days_to_expiry']

        style = get_line_style(idx)

        fig.add_trace(go.Scatter(
            x=strikes,
            y=pdf,
            mode='lines',
            name=f"{days}D ({exp_date})",
            line=style,
            hovertemplate=format_hover_template(
                "Strike",
                "Probability",
                {'Expiration': exp_date, 'DTE': f'{days} days'}
            )
        ))

    # Add spot price indicator
    fig.add_vline(
        x=spot_price,
        line_dash="dash",
        line_color=DARK_THEME['success'],
        line_width=2,
        annotation_text=f"Spot: ${spot_price:.2f}",
        annotation_position="top"
    )

    # Layout
    layout = create_base_layout(
        title=title,
        xaxis_title="Strike Price ($)",
        yaxis_title="Probability Density",
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(20,20,20,0.8)',
            bordercolor=DARK_THEME['grid'],
            borderwidth=1
        )
    )

    fig.update_layout(**layout)

    return fig


def plot_cdf(
    strikes: np.ndarray,
    cdf: np.ndarray,
    spot_price: float,
    title: str = "Cumulative Distribution Function",
    show_percentiles: bool = True
) -> go.Figure:
    """
    Plot cumulative distribution function.

    Args:
        strikes: Strike prices
        cdf: CDF values (0 to 1)
        spot_price: Current spot price
        title: Plot title
        show_percentiles: Whether to show key percentile lines

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Main CDF line
    fig.add_trace(go.Scatter(
        x=strikes,
        y=cdf * 100,  # Convert to percentage
        mode='lines',
        name='CDF',
        line=dict(
            color=DARK_THEME['secondary'],
            width=3
        ),
        hovertemplate=format_hover_template("Strike", "Cumulative Probability (%)")
    ))

    # Add spot price indicator
    fig.add_vline(
        x=spot_price,
        line_dash="dash",
        line_color=DARK_THEME['success'],
        line_width=2,
        annotation_text=f"Spot: ${spot_price:.2f}",
        annotation_position="top"
    )

    # Add percentile lines
    if show_percentiles:
        percentiles = [25, 50, 75]
        for p in percentiles:
            strike_at_p = np.interp(p / 100, cdf, strikes)

            fig.add_hline(
                y=p,
                line_dash="dot",
                line_color=DARK_THEME['neutral'],
                line_width=1,
                annotation_text=f"P{p}",
                annotation_position="right"
            )

            fig.add_vline(
                x=strike_at_p,
                line_dash="dot",
                line_color=DARK_THEME['neutral'],
                line_width=1,
                annotation_text=f"${strike_at_p:.0f}",
                annotation_position="top"
            )

    # Layout
    layout = create_base_layout(
        title=title,
        xaxis_title="Strike Price ($)",
        yaxis_title="Cumulative Probability (%)",
        showlegend=False
    )

    # Set y-axis range to 0-100%
    layout['yaxis']['range'] = [0, 100]

    fig.update_layout(**layout)

    return fig


def plot_pdf_vs_normal(
    strikes: np.ndarray,
    pdf: np.ndarray,
    mean: float,
    std: float,
    spot_price: float,
    title: str = "PDF vs Normal Distribution"
) -> go.Figure:
    """
    Compare PDF to normal distribution with same mean and std.

    Args:
        strikes: Strike prices
        pdf: Actual PDF values
        mean: PDF mean
        std: PDF standard deviation
        spot_price: Current spot price
        title: Plot title

    Returns:
        Plotly figure
    """
    from scipy.stats import norm

    fig = go.Figure()

    # Actual PDF
    fig.add_trace(go.Scatter(
        x=strikes,
        y=pdf,
        mode='lines',
        name='Market PDF',
        line=dict(
            color=DARK_THEME['primary'],
            width=3
        ),
        hovertemplate=format_hover_template("Strike", "Probability Density")
    ))

    # Normal distribution
    normal_pdf = norm.pdf(strikes, loc=mean, scale=std)

    fig.add_trace(go.Scatter(
        x=strikes,
        y=normal_pdf,
        mode='lines',
        name='Normal Distribution',
        line=dict(
            color=DARK_THEME['warning'],
            width=2,
            dash='dash'
        ),
        hovertemplate=format_hover_template("Strike", "Normal PDF")
    ))

    # Add spot price indicator
    fig.add_vline(
        x=spot_price,
        line_dash="dot",
        line_color=DARK_THEME['success'],
        line_width=2,
        annotation_text=f"Spot: ${spot_price:.2f}",
        annotation_position="top"
    )

    # Layout
    layout = create_base_layout(
        title=title,
        xaxis_title="Strike Price ($)",
        yaxis_title="Probability Density",
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(20,20,20,0.8)',
            bordercolor=DARK_THEME['grid'],
            borderwidth=1
        )
    )

    fig.update_layout(**layout)

    return fig


if __name__ == "__main__":
    # Test 2D PDF plots
    print("Testing 2D PDF plots...")

    # Create synthetic PDF data
    spot = 450.0
    strikes = np.linspace(400, 500, 200)
    mean = spot
    std = 15

    # Lognormal-like PDF
    from scipy.stats import norm
    pdf = norm.pdf(strikes, loc=mean, scale=std)

    # Test single PDF plot
    fig1 = plot_pdf_2d(strikes, pdf, spot)
    fig1.write_html("test_pdf_2d.html")
    print("✅ 2D PDF plot saved to test_pdf_2d.html")

    # Test CDF plot
    try:
        from scipy.integrate import cumulative_trapezoid
    except ImportError:
        from scipy.integrate import cumtrapz as cumulative_trapezoid
    cdf = cumulative_trapezoid(pdf, strikes, initial=0)
    cdf = cdf / cdf[-1]

    fig2 = plot_cdf(strikes, cdf, spot)
    fig2.write_html("test_cdf.html")
    print("✅ CDF plot saved to test_cdf.html")

    # Test comparison plot
    pdf_data = {
        '2025-01-15': {
            'strikes': strikes,
            'pdf': norm.pdf(strikes, mean, std * 0.8),
            'days_to_expiry': 15
        },
        '2025-02-01': {
            'strikes': strikes,
            'pdf': norm.pdf(strikes, mean, std),
            'days_to_expiry': 30
        },
        '2025-03-01': {
            'strikes': strikes,
            'pdf': norm.pdf(strikes, mean, std * 1.2),
            'days_to_expiry': 60
        }
    }

    fig3 = plot_pdf_comparison(pdf_data, spot)
    fig3.write_html("test_pdf_comparison.html")
    print("✅ PDF comparison saved to test_pdf_comparison.html")

    # Test PDF vs Normal
    fig4 = plot_pdf_vs_normal(strikes, pdf, mean, std, spot)
    fig4.write_html("test_pdf_vs_normal.html")
    print("✅ PDF vs Normal saved to test_pdf_vs_normal.html")

    print("\n✅ All 2D PDF visualization tests passed!")
