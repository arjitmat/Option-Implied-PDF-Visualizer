"""
Visualization theme configuration for consistent dark theme styling across all plots.
"""

from typing import Dict
import plotly.graph_objects as go
from config.constants import PLOT_WIDTH, PLOT_HEIGHT, PLOT_COLORSCALE, PLOT_BG_COLOR


# Dark theme colors
DARK_THEME = {
    'background': 'rgb(20,20,20)',
    'paper': 'rgb(20,20,20)',
    'plot_bg': 'rgb(30,30,30)',
    'grid': 'rgb(50,50,50)',
    'text': 'rgb(220,220,220)',
    'primary': '#00D9FF',  # Cyan
    'secondary': '#FF00FF',  # Magenta
    'success': '#00FF88',  # Green
    'warning': '#FFD700',  # Gold
    'danger': '#FF4444',  # Red
    'neutral': 'rgb(150,150,150)'
}

# Colorscales
COLORSCALES = {
    'viridis': 'Viridis',
    'plasma': 'Plasma',
    'inferno': 'Inferno',
    'magma': 'Magma',
    'cividis': 'Cividis',
    'turbo': 'Turbo',
    'rainbow': 'Rainbow',
    'jet': 'Jet',
    'portland': 'Portland',
    'picnic': 'Picnic'
}

# Default layout template
DEFAULT_LAYOUT = {
    'paper_bgcolor': DARK_THEME['background'],
    'plot_bgcolor': DARK_THEME['plot_bg'],
    'font': {
        'color': DARK_THEME['text'],
        'family': 'Arial, sans-serif',
        'size': 12
    },
    'title': {
        'font': {
            'size': 18,
            'color': DARK_THEME['text']
        }
    },
    'xaxis': {
        'gridcolor': DARK_THEME['grid'],
        'zerolinecolor': DARK_THEME['grid'],
        'color': DARK_THEME['text']
    },
    'yaxis': {
        'gridcolor': DARK_THEME['grid'],
        'zerolinecolor': DARK_THEME['grid'],
        'color': DARK_THEME['text']
    },
    'width': PLOT_WIDTH,
    'height': PLOT_HEIGHT,
    'hovermode': 'closest'
}


def apply_dark_theme(fig: go.Figure, **kwargs) -> go.Figure:
    """
    Apply dark theme to a Plotly figure.

    Args:
        fig: Plotly figure
        **kwargs: Additional layout parameters to override defaults

    Returns:
        Figure with dark theme applied
    """
    layout_updates = DEFAULT_LAYOUT.copy()
    layout_updates.update(kwargs)

    fig.update_layout(**layout_updates)

    return fig


def create_base_layout(
    title: str = "",
    xaxis_title: str = "",
    yaxis_title: str = "",
    **kwargs
) -> Dict:
    """
    Create base layout configuration with dark theme.

    Args:
        title: Plot title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        **kwargs: Additional layout parameters

    Returns:
        Layout dictionary
    """
    layout = DEFAULT_LAYOUT.copy()

    layout.update({
        'title': title,
        'xaxis': {
            **layout['xaxis'],
            'title': xaxis_title
        },
        'yaxis': {
            **layout['yaxis'],
            'title': yaxis_title
        }
    })

    layout.update(kwargs)

    return layout


def get_line_style(index: int) -> Dict:
    """
    Get line style for multi-line plots.

    Args:
        index: Line index (0-based)

    Returns:
        Dictionary with color and dash pattern
    """
    colors = [
        DARK_THEME['primary'],
        DARK_THEME['secondary'],
        DARK_THEME['success'],
        DARK_THEME['warning'],
        DARK_THEME['danger'],
        '#00FFFF',  # Cyan
        '#FF1493',  # Deep Pink
        '#00FF00',  # Lime
        '#FFA500',  # Orange
        '#9370DB'   # Medium Purple
    ]

    dash_patterns = ['solid', 'dash', 'dot', 'dashdot']

    return {
        'color': colors[index % len(colors)],
        'dash': dash_patterns[(index // len(colors)) % len(dash_patterns)],
        'width': 2
    }


def format_hover_template(
    x_label: str = "X",
    y_label: str = "Y",
    extra_fields: Dict[str, str] = None
) -> str:
    """
    Create hover template for consistent hover display.

    Args:
        x_label: Label for x-axis value
        y_label: Label for y-axis value
        extra_fields: Additional fields to display

    Returns:
        Hover template string
    """
    template = f"<b>{x_label}:</b> %{{x}}<br>"
    template += f"<b>{y_label}:</b> %{{y}}<br>"

    if extra_fields:
        for label, value_key in extra_fields.items():
            template += f"<b>{label}:</b> {value_key}<br>"

    template += "<extra></extra>"  # Remove trace name

    return template


# 3D scene configuration
SCENE_3D_CONFIG = {
    'bgcolor': DARK_THEME['plot_bg'],
    'xaxis': {
        'backgroundcolor': DARK_THEME['plot_bg'],
        'gridcolor': DARK_THEME['grid'],
        'showbackground': True,
        'zerolinecolor': DARK_THEME['grid'],
        'color': DARK_THEME['text']
    },
    'yaxis': {
        'backgroundcolor': DARK_THEME['plot_bg'],
        'gridcolor': DARK_THEME['grid'],
        'showbackground': True,
        'zerolinecolor': DARK_THEME['grid'],
        'color': DARK_THEME['text']
    },
    'zaxis': {
        'backgroundcolor': DARK_THEME['plot_bg'],
        'gridcolor': DARK_THEME['grid'],
        'showbackground': True,
        'zerolinecolor': DARK_THEME['grid'],
        'color': DARK_THEME['text']
    }
}


def create_3d_scene_config(
    xaxis_title: str = "X",
    yaxis_title: str = "Y",
    zaxis_title: str = "Z",
    **kwargs
) -> Dict:
    """
    Create 3D scene configuration.

    Args:
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        zaxis_title: Z-axis label
        **kwargs: Additional scene parameters

    Returns:
        Scene configuration dictionary
    """
    scene = SCENE_3D_CONFIG.copy()
    scene['xaxis']['title'] = xaxis_title
    scene['yaxis']['title'] = yaxis_title
    scene['zaxis']['title'] = zaxis_title

    scene.update(kwargs)

    return scene


# Export all theme components
__all__ = [
    'DARK_THEME',
    'COLORSCALES',
    'DEFAULT_LAYOUT',
    'SCENE_3D_CONFIG',
    'apply_dark_theme',
    'create_base_layout',
    'get_line_style',
    'format_hover_template',
    'create_3d_scene_config'
]


if __name__ == "__main__":
    # Test theme configuration
    import plotly.graph_objects as go
    import numpy as np

    print("Testing theme configuration...")

    # Create sample plot
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    fig = go.Figure()

    # Add traces with themed styles
    style1 = get_line_style(0)
    style2 = get_line_style(1)

    fig.add_trace(go.Scatter(
        x=x, y=y1, name='Sin',
        line=style1,
        hovertemplate=format_hover_template("X", "Sin(X)")
    ))

    fig.add_trace(go.Scatter(
        x=x, y=y2, name='Cos',
        line=style2,
        hovertemplate=format_hover_template("X", "Cos(X)")
    ))

    # Apply dark theme
    layout = create_base_layout(
        title="Theme Test Plot",
        xaxis_title="X Value",
        yaxis_title="Y Value"
    )

    fig.update_layout(**layout)

    # Save test
    fig.write_html("test_theme.html")
    print("✅ Theme test saved to test_theme.html")
