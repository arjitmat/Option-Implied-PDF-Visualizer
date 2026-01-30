"""
3D probability surface visualization.

Create interactive 3D surface plots showing Strike × Time-to-Expiry × Probability.
"""

import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Optional
from src.visualization.themes import (
    create_base_layout,
    create_3d_scene_config,
    DARK_THEME,
    COLORSCALES
)


def create_3d_surface(
    pdf_data: Dict[str, Dict[str, np.ndarray]],
    spot_price: Optional[float] = None,
    title: str = "SPX Option-Implied Probability Surface",
    colorscale: str = 'Viridis',
    show_contours: bool = True
) -> go.Figure:
    """
    Create 3D probability surface from multiple expiration PDFs.

    Args:
        pdf_data: Dictionary with format:
            {
                'expiration_date': {
                    'strikes': np.ndarray,
                    'pdf': np.ndarray,
                    'days_to_expiry': int
                }
            }
        spot_price: Current spot price (optional, for marker)
        title: Plot title
        colorscale: Plotly colorscale name
        show_contours: Whether to show contour lines

    Returns:
        Plotly 3D figure
    """
    if len(pdf_data) < 2:
        raise ValueError("Need at least 2 expirations for 3D surface")

    # Sort by days to expiry
    sorted_data = sorted(
        pdf_data.items(),
        key=lambda x: x[1]['days_to_expiry']
    )

    # Find common strike range
    all_strikes = [data['strikes'] for _, data in sorted_data]
    min_strike = max(strikes.min() for strikes in all_strikes)
    max_strike = min(strikes.max() for strikes in all_strikes)

    # Create uniform strike grid
    strike_grid = np.linspace(min_strike, max_strike, 100)

    # Prepare data for surface
    expiry_days = []
    pdf_matrix = []

    for exp_date, data in sorted_data:
        days = data['days_to_expiry']
        strikes = data['strikes']
        pdf = data['pdf']

        # Interpolate to uniform grid
        pdf_interp = np.interp(strike_grid, strikes, pdf)

        expiry_days.append(days)
        pdf_matrix.append(pdf_interp)

    # Convert to 2D arrays
    X = strike_grid  # Strikes
    Y = np.array(expiry_days)  # Days to expiry
    Z = np.array(pdf_matrix)  # PDF values

    # Create meshgrid
    X_mesh, Y_mesh = np.meshgrid(X, Y)

    # Create figure
    fig = go.Figure()

    # Add surface
    contours_config = {}
    if show_contours:
        contours_config = {
            'z': {
                'show': True,
                'usecolormap': True,
                'highlightcolor': "limegreen",
                'project': {'z': True}
            }
        }

    fig.add_trace(go.Surface(
        x=X_mesh,
        y=Y_mesh,
        z=Z,
        colorscale=colorscale,
        opacity=0.9,
        name='Probability Density',
        contours=contours_config,
        hovertemplate=(
            '<b>Strike:</b> $%{x:.2f}<br>'
            '<b>Days to Expiry:</b> %{y:.0f}<br>'
            '<b>Probability Density:</b> %{z:.6f}<br>'
            '<extra></extra>'
        )
    ))

    # Add spot price marker (vertical line) if provided
    if spot_price is not None:
        # Create vertical line at spot price
        z_line = np.linspace(0, Z.max(), 10)
        y_line = np.full_like(z_line, Y.min())
        x_line = np.full_like(z_line, spot_price)

        fig.add_trace(go.Scatter3d(
            x=x_line,
            y=y_line,
            z=z_line,
            mode='lines',
            name=f'Spot: ${spot_price:.2f}',
            line=dict(
                color=DARK_THEME['success'],
                width=5,
                dash='dash'
            ),
            showlegend=True
        ))

    # Configure 3D scene
    scene = create_3d_scene_config(
        xaxis_title="Strike Price ($)",
        yaxis_title="Days to Expiration",
        zaxis_title="Probability Density"
    )

    # Layout
    layout = create_base_layout(
        title=title,
        showlegend=True,
        scene=scene,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(20,20,20,0.8)',
            bordercolor=DARK_THEME['grid'],
            borderwidth=1
        )
    )

    fig.update_layout(**layout)

    # Set camera angle for better view
    fig.update_layout(
        scene_camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.3),
            center=dict(x=0, y=0, z=-0.1)
        )
    )

    return fig


def create_heatmap_2d(
    pdf_data: Dict[str, Dict[str, np.ndarray]],
    spot_price: Optional[float] = None,
    title: str = "Probability Density Heatmap",
    colorscale: str = 'Viridis'
) -> go.Figure:
    """
    Create 2D heatmap of probability density (alternative to 3D surface).

    Args:
        pdf_data: PDF data for multiple expirations
        spot_price: Current spot price
        title: Plot title
        colorscale: Plotly colorscale name

    Returns:
        Plotly figure
    """
    if len(pdf_data) < 2:
        raise ValueError("Need at least 2 expirations for heatmap")

    # Sort by days to expiry
    sorted_data = sorted(
        pdf_data.items(),
        key=lambda x: x[1]['days_to_expiry']
    )

    # Find common strike range
    all_strikes = [data['strikes'] for _, data in sorted_data]
    min_strike = max(strikes.min() for strikes in all_strikes)
    max_strike = min(strikes.max() for strikes in all_strikes)

    # Create uniform strike grid
    strike_grid = np.linspace(min_strike, max_strike, 100)

    # Prepare data
    expiry_labels = []
    pdf_matrix = []

    for exp_date, data in sorted_data:
        days = data['days_to_expiry']
        strikes = data['strikes']
        pdf = data['pdf']

        # Interpolate to uniform grid
        pdf_interp = np.interp(strike_grid, strikes, pdf)

        expiry_labels.append(f"{days}D")
        pdf_matrix.append(pdf_interp)

    # Transpose for correct orientation
    Z = np.array(pdf_matrix)

    # Create heatmap
    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        x=strike_grid,
        y=expiry_labels,
        z=Z,
        colorscale=colorscale,
        colorbar=dict(
            title="Probability<br>Density",
            titleside="right"
        ),
        hovertemplate=(
            '<b>Strike:</b> $%{x:.2f}<br>'
            '<b>Expiration:</b> %{y}<br>'
            '<b>Probability:</b> %{z:.6f}<br>'
            '<extra></extra>'
        )
    ))

    # Add spot price line
    if spot_price is not None:
        fig.add_vline(
            x=spot_price,
            line_dash="dash",
            line_color=DARK_THEME['success'],
            line_width=3,
            annotation_text=f"Spot: ${spot_price:.2f}",
            annotation_position="top"
        )

    # Layout
    layout = create_base_layout(
        title=title,
        xaxis_title="Strike Price ($)",
        yaxis_title="Days to Expiration"
    )

    fig.update_layout(**layout)

    return fig


def create_wireframe_3d(
    pdf_data: Dict[str, Dict[str, np.ndarray]],
    spot_price: Optional[float] = None,
    title: str = "Probability Wireframe",
    line_color: str = None
) -> go.Figure:
    """
    Create 3D wireframe plot (lighter alternative to surface).

    Args:
        pdf_data: PDF data for multiple expirations
        spot_price: Current spot price
        title: Plot title
        line_color: Line color (default: cyan)

    Returns:
        Plotly figure
    """
    if line_color is None:
        line_color = DARK_THEME['primary']

    # Sort by days to expiry
    sorted_data = sorted(
        pdf_data.items(),
        key=lambda x: x[1]['days_to_expiry']
    )

    fig = go.Figure()

    # Add each expiration as a 3D line
    for idx, (exp_date, data) in enumerate(sorted_data):
        strikes = data['strikes']
        pdf = data['pdf']
        days = data['days_to_expiry']

        # Create y-values (all same for this expiration)
        y_vals = np.full_like(strikes, days)

        fig.add_trace(go.Scatter3d(
            x=strikes,
            y=y_vals,
            z=pdf,
            mode='lines',
            name=f"{days}D",
            line=dict(
                color=line_color,
                width=2
            ),
            hovertemplate=(
                f'<b>Strike:</b> %{{x:.2f}}<br>'
                f'<b>Days:</b> {days}<br>'
                f'<b>PDF:</b> %{{z:.6f}}<br>'
                '<extra></extra>'
            )
        ))

    # Configure 3D scene
    scene = create_3d_scene_config(
        xaxis_title="Strike Price ($)",
        yaxis_title="Days to Expiration",
        zaxis_title="Probability Density"
    )

    # Layout
    layout = create_base_layout(
        title=title,
        showlegend=True,
        scene=scene,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(20,20,20,0.8)',
            bordercolor=DARK_THEME['grid'],
            borderwidth=1
        )
    )

    fig.update_layout(**layout)

    # Set camera angle
    fig.update_layout(
        scene_camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.3)
        )
    )

    return fig


if __name__ == "__main__":
    # Test 3D surface plots
    print("Testing 3D probability surface...")

    # Create synthetic PDF data for multiple expirations
    from scipy.stats import norm

    spot = 450.0
    strikes_base = np.linspace(400, 500, 100)

    # Create PDFs for different expirations
    pdf_data = {}

    expirations = [
        ('2025-01-15', 15),
        ('2025-02-01', 30),
        ('2025-02-15', 45),
        ('2025-03-01', 60)
    ]

    for exp_date, days in expirations:
        # Adjust std based on time (more spread for longer dated)
        std = 10 * np.sqrt(days / 30)
        pdf = norm.pdf(strikes_base, loc=spot, scale=std)

        pdf_data[exp_date] = {
            'strikes': strikes_base,
            'pdf': pdf,
            'days_to_expiry': days
        }

    # Test 3D surface
    fig1 = create_3d_surface(pdf_data, spot_price=spot)
    fig1.write_html("test_3d_surface.html")
    print("✅ 3D surface saved to test_3d_surface.html")

    # Test heatmap
    fig2 = create_heatmap_2d(pdf_data, spot_price=spot)
    fig2.write_html("test_heatmap.html")
    print("✅ Heatmap saved to test_heatmap.html")

    # Test wireframe
    fig3 = create_wireframe_3d(pdf_data, spot_price=spot)
    fig3.write_html("test_wireframe.html")
    print("✅ Wireframe saved to test_wireframe.html")

    print("\n✅ All 3D visualization tests passed!")
