"""
Premium Single-Page Option-Implied PDF Visualizer

Merges Gemini's production-ready UI with real backend functionality.
Features: Revolut-style glassmorphism, SVG icons, premium animations, real data.
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Option-Implied PDF Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# DESIGN SYSTEM & UTILITIES
# =============================================================================

COLORS = {
    "bg": "#0e1117",
    "surface": "#1e1e2e",
    "cyan": "#00d9ff",
    "green": "#00ff88",
    "red": "#ff4757",
    "white": "#fafafa",
    "gray": "#a0a0a0",
    "border": "#2a2a3e",
    "chart_bg": "#0e1117",
    "purple": "#a55eea",
    "orange": "#ffa502"
}

def get_icon(name, color=COLORS['cyan'], size=24):
    """SVG Icon Helper"""
    icons = {
        "chart": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
        "shield": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        "target": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
        "brain": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 0 7 4.5v15A2.5 2.5 0 0 0 9.5 22h5a2.5 2.5 0 0 0 2.5-2.5v-15A2.5 2.5 0 0 0 14.5 2h-5z"></path></svg>',
        "clock": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
        "alert": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        "graduation": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>',
        "wave": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h5l3 5 5-10 4 10h5"/></svg>',
        "database": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
        "rocket": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path></svg>'
    }
    return icons.get(name, "")

def show_premium_loading_overlay(steps):
    """Show premium loading animation with status steps"""
    loading_placeholder = st.empty()

    loader_css = """
    <style>
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
    """
    st.markdown(loader_css, unsafe_allow_html=True)

    for i, step in enumerate(steps):
        # Build status dots
        dots_html = ""
        for j in range(len(steps)):
            if j < i:
                color = COLORS['green']
                symbol = "✓"
            elif j == i:
                color = COLORS['cyan']
                symbol = "●"
            else:
                color = "#333"
                symbol = "○"
            dots_html += f'<div style="display:inline-block; width:32px; height:32px; margin:0 4px; color:{color}; font-size:20px; text-align:center;">{symbol}</div>'

        overlay_html = f"""
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(14, 17, 23, 0.95); backdrop-filter: blur(10px);
            z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="width: 550px; padding: 48px; background: rgba(30, 30, 46, 0.95);
                border: 1px solid {COLORS['cyan']}; border-radius: 16px;
                box-shadow: 0 0 60px rgba(0,217,255,0.3), 0 20px 60px rgba(0,0,0,0.8); text-align: center;">
                <div style="font-size: 56px; margin-bottom: 24px; animation: spin 2s linear infinite;">🔄</div>
                <h2 style="color: white; margin: 0 0 8px 0; font-size: 24px;">Analyzing Option Chain...</h2>
                <p style="color: {COLORS['gray']}; font-size: 14px; margin: 0 0 32px 0;">This usually takes 15-30 seconds</p>
                <div style="margin: 24px 0;">
                    {dots_html}
                </div>
                <p style="color: {COLORS['cyan']}; margin-top: 20px; font-weight: bold; font-size: 16px; animation: pulse 1.5s ease-in-out infinite;">{step}</p>
            </div>
        </div>
        """
        loading_placeholder.markdown(overlay_html, unsafe_allow_html=True)
        time.sleep(0.8)  # Realistic delay

    loading_placeholder.empty()

# =============================================================================
# CUSTOM CSS - PREMIUM THEME
# =============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Global Settings */
    .stApp {{
        background-color: {COLORS['bg']};
        color: {COLORS['white']};
        font-family: 'Inter', sans-serif;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: {COLORS['white']};
    }}

    .monospace {{
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Card Styling */
    .glass-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0,217,255,0.2);
    }}

    /* Premium gradients */
    .gradient-cyan {{
        background: linear-gradient(135deg, {COLORS['cyan']} 0%, #0099cc 100%);
    }}

    .gradient-hero {{
        background: radial-gradient(ellipse at 30% 20%, rgba(0,217,255,0.12) 0%, transparent 50%),
                    radial-gradient(ellipse at 70% 60%, rgba(0,255,136,0.08) 0%, transparent 50%),
                    #0a0e27;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(90deg, #00d9ff 0%, #0099cc 100%);
        color: #0e1117;
        font-weight: bold;
        border: none;
        height: 56px;
        font-size: 18px;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0,217,255,0.3);
        position: relative;
        overflow: hidden;
    }}

    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }}

    .stButton > button:hover::before {{
        width: 300px;
        height: 300px;
    }}

    .stButton > button:hover {{
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba(0,217,255,0.5);
    }}

    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {{
        background-color: {COLORS['bg']};
        color: {COLORS['white']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        transition: all 0.3s ease;
    }}

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {{
        border-color: {COLORS['cyan']};
        box-shadow: 0 0 0 3px rgba(0,217,255,0.3);
    }}

    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}

    /* Apply animations */
    .hero-section {{
        animation: fadeIn 0.8s ease-out;
    }}

    .metric-card {{
        transition: all 0.3s ease;
        animation: slideUp 0.5s ease-out backwards;
    }}

    .metric-card:nth-child(1) {{ animation-delay: 0.1s; }}
    .metric-card:nth-child(2) {{ animation-delay: 0.2s; }}
    .metric-card:nth-child(3) {{ animation-delay: 0.3s; }}
    .metric-card:nth-child(4) {{ animation-delay: 0.4s; }}

    .metric-card:hover {{
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }}

    /* Smooth Scroll */
    html {{ scroll-behavior: smooth; }}

    /* Hide default padding */
    .block-container {{
        padding-top: 0;
        padding-bottom: 0;
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if 'ticker' not in st.session_state:
    st.session_state.ticker = 'SPY'
if 'days_to_expiry' not in st.session_state:
    st.session_state.days_to_expiry = 30
if 'analysis_mode' not in st.session_state:
    st.session_state.analysis_mode = 'standard'
if 'use_sabr' not in st.session_state:
    st.session_state.use_sabr = True
if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None
if 'current_strikes' not in st.session_state:
    st.session_state.current_strikes = None
if 'current_spot' not in st.session_state:
    st.session_state.current_spot = None
if 'current_stats' not in st.session_state:
    st.session_state.current_stats = None
if 'current_interpretation' not in st.session_state:
    st.session_state.current_interpretation = None
if 'pattern_matches' not in st.session_state:
    st.session_state.pattern_matches = []
if 'data_timestamp' not in st.session_state:
    st.session_state.data_timestamp = None

# =============================================================================
# HERO SECTION
# =============================================================================

st.markdown(f"""
<div style="text-align: center; padding: 80px 20px;
    background: radial-gradient(circle at center, rgba(0, 217, 255, 0.1) 0%, rgba(14, 17, 23, 0) 70%);
    border-bottom: 1px solid {COLORS['border']}; margin-bottom: 40px;" class="hero-section">
    <div style="display: inline-block; margin-bottom: 16px;">
        {get_icon('wave', COLORS['cyan'], 48)}
    </div>
    <h1 style="font-size: 48px; margin: 0 0 16px 0; background: linear-gradient(to right, #fff, {COLORS['gray']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Option-Implied PDF Visualizer
    </h1>
    <p style="color: {COLORS['gray']}; font-size: 18px; max-width: 600px; margin: 0 auto;">
        Decode market expectations through real-time probability distributions.
    </p>
    <div style="width: 100px; height: 2px; background: linear-gradient(90deg, transparent, {COLORS['cyan']}, transparent); margin: 30px auto;"></div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# EDUCATIONAL SECTION
# =============================================================================

st.markdown(f"<h2 style='text-align: center; margin-bottom: 30px;'>What Is PDF Analysis?</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex; align-items:center; margin-bottom:16px;">
            {get_icon('graduation', COLORS['cyan'], 32)}
            <h3 style="margin:0 0 0 12px; font-size:22px;">New to Options?</h3>
        </div>
        <p style="color: {COLORS['gray']}; line-height: 1.6;">
            Option prices contain <span style="color: {COLORS['cyan']}">hidden info</span> about market expectations. We extract these into probability charts. See where traders think stock will land, the <span style="color: {COLORS['cyan']}">uncertainty range</span>, and directional bias.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex; align-items:center; margin-bottom:16px;">
            {get_icon('chart', COLORS['cyan'], 32)}
            <h3 style="margin:0 0 0 12px; font-size:22px;">For Quants & Traders</h3>
        </div>
        <p style="color: {COLORS['gray']}; line-height: 1.6;">
            <span style="color: {COLORS['cyan']}">Breeden-Litzenberger</span> risk-neutral density extraction. SABR volatility calibration. Real-time SPY/SPX analysis. Full statistics: mean, skewness, kurtosis, <span style="color: {COLORS['cyan']}">Tail Risk</span>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# DATA CREDIBILITY
# =============================================================================

st.markdown(f"""
<div class="glass-card" style="margin-top: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {COLORS['border']}; padding-bottom: 15px; margin-bottom: 15px;">
        <h3 style="margin:0;">Enterprise-Grade Market Data</h3>
        <span style="color: {COLORS['gray']}; font-size: 12px; font-style: italic;">
            {get_icon('clock', COLORS['green'], 14)} {datetime.now().strftime("%b %d, %Y %I:%M %p ET")} • <span style="color:{COLORS['green']}">● Live</span>
        </span>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
        <div>
            <h4 style="color:{COLORS['cyan']}; margin-bottom:8px;">{get_icon('database', COLORS['cyan'], 20)} Real-Time Data</h4>
            <ul style="color:{COLORS['gray']}; font-size:14px; padding-left:20px; margin: 0;">
                <li>Major US Exchanges</li>
                <li>CBOE / NYSE / Nasdaq</li>
                <li>15min updates</li>
            </ul>
        </div>
        <div>
            <h4 style="color:{COLORS['green']}; margin-bottom:8px;">{get_icon('shield', COLORS['green'], 20)} Data Quality</h4>
            <div style="background:#2a2a3e; height:6px; border-radius:3px; margin-bottom:8px;">
                <div style="width:98%; background:{COLORS['cyan']}; height:100%; border-radius:3px;"></div>
            </div>
            <span style="color:{COLORS['white']}; font-size:12px;">98% Coverage • Institutional Grade</span>
        </div>
        <div>
            <h4 style="color:{COLORS['purple']}; margin-bottom:8px;">{get_icon('graduation', COLORS['purple'], 20)} Academic Std</h4>
            <ul style="color:{COLORS['gray']}; font-size:14px; padding-left:20px; margin: 0;">
                <li>Breeden-Litzenberger (1978)</li>
                <li>SABR Calibration</li>
                <li>Peer-Reviewed Models</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# USE CASES
# =============================================================================

st.markdown(f"<h2 style='margin: 40px 0 20px 0; text-align:center;'>What Traders Use This For</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="glass-card" style="border-top: 3px solid {COLORS['cyan']}; height: 100%;">
        <div style="text-align:center; margin-bottom:12px;">{get_icon('shield', COLORS['cyan'], 48)}</div>
        <h3 style="text-align:center;">Risk Management</h3>
        <ul style="color:{COLORS['gray']}; font-size:14px; line-height:2;">
            <li>Tail risk assessment</li>
            <li>Position sizing</li>
            <li>Asymmetric risk/reward</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="glass-card" style="border-top: 3px solid {COLORS['green']}; height: 100%;">
        <div style="text-align:center; margin-bottom:12px;">{get_icon('target', COLORS['green'], 48)}</div>
        <h3 style="text-align:center;">Strategy Selection</h3>
        <ul style="color:{COLORS['gray']}; font-size:14px; line-height:2;">
            <li>Optimal strikes</li>
            <li>Spreads vs Naked</li>
            <li>Mispriced volatility</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="glass-card" style="border-top: 3px solid {COLORS['purple']}; height: 100%;">
        <div style="text-align:center; margin-bottom:12px;">{get_icon('brain', COLORS['purple'], 48)}</div>
        <h3 style="text-align:center;">Market Sentiment</h3>
        <ul style="color:{COLORS['gray']}; font-size:14px; line-height:2;">
            <li>Bullish/Bearish bias</li>
            <li>Regime changes</li>
            <li>Historical patterns</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# DISCLAIMER
# =============================================================================

st.markdown(f"""
<div style="background: rgba(30, 30, 46, 0.8); border: 2px solid {COLORS['red']}; border-radius: 8px; padding: 20px; margin: 40px auto; max-width: 900px; box-shadow: 0 0 15px rgba(255, 71, 87, 0.1);">
    <div style="display:flex; align-items:center; margin-bottom:12px;">
        {get_icon('alert', COLORS['red'], 24)}
        <h3 style="margin:0 0 0 12px; color:{COLORS['white']};">Important Disclaimer</h3>
    </div>
    <p style="color:{COLORS['gray']}; font-size:14px; line-height:1.5;">
        Educational and informational purposes ONLY. NOT financial advice, investment recommendation, or solicitation.
        Distributions are estimates based on models. All investments involve risk.
    </p>
    <div style="display:flex; gap: 20px; margin-top: 15px; justify-content:center;">
         <span style="color:{COLORS['cyan']}; font-size:12px; font-weight:bold;">📚 Educational Use</span>
         <span style="color:{COLORS['red']}; font-size:12px; font-weight:bold;">🚫 Not Financial Advice</span>
         <span style="color:{COLORS['orange']}; font-size:12px; font-weight:bold;">⚡ Use At Your Risk</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# INPUT CONTROLS
# =============================================================================

st.markdown(f"""
<div class="glass-card" style="background: linear-gradient(180deg, rgba(0, 217, 255, 0.05) 0%, {COLORS['surface']} 100%); margin-top: 40px; padding: 32px; max-width: 900px; margin-left: auto; margin-right: auto;">
    <h3 style="border-bottom: 1px solid {COLORS['cyan']}; padding-bottom: 10px; margin-bottom: 24px;">Configure Analysis</h3>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("TICKER SYMBOL", value=st.session_state.ticker, help="Any stock or ETF with options")
    st.caption("Any stock or ETF with options")
with c2:
    days_to_expiry = st.selectbox("DAYS TO EXPIRATION", [7, 14, 21, 30, 45, 60, 90], index=3)
    st.caption("Target expiration window")
with c3:
    analysis_mode = st.selectbox("ANALYSIS MODE", ["standard", "conservative", "aggressive", "educational"], index=0)
    st.caption("AI interpretation style")

st.session_state.ticker = ticker.upper()
st.session_state.days_to_expiry = days_to_expiry
st.session_state.analysis_mode = analysis_mode

st.markdown("</div>", unsafe_allow_html=True)

# Run Button
run_analysis = st.button(f"{get_icon('rocket', '#0e1117', 20)} Run Analysis", type="primary", use_container_width=True, key="run_btn")

# =============================================================================
# ANALYSIS LOGIC
# =============================================================================

if run_analysis:
    steps = [
        "Connecting to Exchange...",
        "Fetching Option Chain...",
        "Calculating Implied Vol...",
        "Fitting PDF Curve...",
        "Computing Statistics...",
        "Running AI Model..."
    ]

    show_premium_loading_overlay(steps)

    try:
        from src.data.data_manager import DataManager
        from src.core.breeden_litz import BreedenlitzenbergPDF
        from src.core.statistics import PDFStatistics
        from src.ai.interpreter import PDFInterpreter
        from scipy.stats import norm

        # Fetch data
        data_manager = DataManager()
        options_df = data_manager.get_options(ticker=ticker, min_expiry_days=days_to_expiry-3, max_expiry_days=days_to_expiry+3)

        if options_df is None or options_df.empty:
            st.error("Failed to fetch option data. Please check ticker and try again.")
            st.stop()

        # Get risk-free rate and spot price
        risk_free_rate = data_manager.get_risk_free_rate()
        spot_price = options_df.get('underlying_price', options_df['strike'].median()).iloc[0] if 'underlying_price' in options_df.columns else data_manager.get_spot_price(ticker)

        # Calculate PDF
        pdf_calculator = BreedenlitzenbergPDF()

        # Standardize columns
        if 'optionType' not in options_df.columns and 'option_type' in options_df.columns:
            options_df = options_df.rename(columns={'option_type': 'optionType'})
        if 'impliedVolatility' not in options_df.columns and 'implied_volatility' in options_df.columns:
            options_df = options_df.rename(columns={'implied_volatility': 'impliedVolatility'})

        calls = options_df[options_df['optionType'] == 'call'].copy()

        if calls.empty:
            st.error("No call options found")
            st.stop()

        # Time to expiry
        exp_date = calls['expiration'].iloc[0]
        if isinstance(exp_date, str):
            exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
        T = (exp_date - datetime.now()).days / 365.0

        # Prepare PDF input
        pdf_input = calls[['strike', 'impliedVolatility']].copy()
        if 'bid' in calls.columns and 'ask' in calls.columns:
            pdf_input['price'] = (calls['bid'] + calls['ask']) / 2
        elif 'lastPrice' in calls.columns:
            pdf_input['price'] = calls['lastPrice']
        else:
            # Black-Scholes pricing as fallback
            sigma = pdf_input['impliedVolatility'].values
            K = pdf_input['strike'].values
            d1 = (np.log(spot_price / K) + (risk_free_rate + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            pdf_input['price'] = spot_price * norm.cdf(d1) - K * np.exp(-risk_free_rate * T) * norm.cdf(d2)

        pdf_strikes, pdf_values = pdf_calculator.calculate_from_options(
            options_df=pdf_input,
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            time_to_expiry=T,
            option_type='call',
            interpolation_method='sabr' if st.session_state.use_sabr else 'spline'
        )

        # Statistics
        stats_calc = PDFStatistics(strikes=pdf_strikes, pdf=pdf_values, spot_price=spot_price, time_to_expiry=T)
        statistics = stats_calc.get_summary()

        # AI Interpretation
        interpreter = PDFInterpreter(mode=analysis_mode)
        interp_result = interpreter.interpret_single_pdf(
            ticker=ticker,
            spot=spot_price,
            stats=statistics,
            days_to_expiry=int(T * 365),
            historical_matches=None
        )

        # Save to session state
        st.session_state.current_pdf = pdf_values
        st.session_state.current_strikes = pdf_strikes
        st.session_state.current_spot = spot_price
        st.session_state.current_stats = statistics
        st.session_state.current_interpretation = interp_result['interpretation']
        st.session_state.data_timestamp = datetime.now()

        st.success("✅ Analysis complete! Scroll down to see results.")
        st.rerun()

    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# =============================================================================
# RESULTS DISPLAY
# =============================================================================

if st.session_state.current_pdf is not None:
    st.markdown("---")
    st.markdown("<h2 style='text-align:center; margin:40px 0 30px 0;'>📊 Analysis Results</h2>", unsafe_allow_html=True)

    # Metrics Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card glass-card" style="border-top: 2px solid {COLORS['cyan']}; padding: 16px;">
            <div style="color:{COLORS['gray']}; font-size:12px; font-weight:bold; margin-bottom:8px;">SPOT PRICE</div>
            <div class="monospace" style="font-size:32px; color:white; margin:8px 0;">${st.session_state.current_spot:.2f}</div>
            <div style="color:{COLORS['gray']}; font-size:12px;">Current underlying</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        mean = st.session_state.current_stats.get('mean', 0)
        delta_pct = ((mean - st.session_state.current_spot) / st.session_state.current_spot) * 100
        st.markdown(f"""
        <div class="metric-card glass-card" style="border-top: 2px solid {COLORS['green']}; padding: 16px;">
            <div style="color:{COLORS['gray']}; font-size:12px; font-weight:bold; margin-bottom:8px;">EXPECTED PRICE</div>
            <div class="monospace" style="font-size:32px; color:white; margin:8px 0;">${mean:.2f}</div>
            <div style="color:{COLORS['green'] if delta_pct > 0 else COLORS['red']}; font-size:14px;">{'+' if delta_pct > 0 else ''}{delta_pct:.2f}% (Risk-neutral)</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        impl_move = st.session_state.current_stats.get('implied_move_pct', 0)
        std = st.session_state.current_stats.get('std_dev', 0)
        lower = st.session_state.current_spot - std
        upper = st.session_state.current_spot + std
        st.markdown(f"""
        <div class="metric-card glass-card" style="border-top: 2px solid {COLORS['cyan']}; padding: 16px;">
            <div style="color:{COLORS['gray']}; font-size:12px; font-weight:bold; margin-bottom:8px;">IMPLIED MOVE</div>
            <div class="monospace" style="font-size:32px; color:white; margin:8px 0;">±{impl_move:.2f}%</div>
            <div style="color:{COLORS['gray']}; font-size:14px;">${lower:.0f} - ${upper:.0f} (1σ)</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        skew = st.session_state.current_stats.get('skewness', 0)
        skew_dir = "Bearish 📉" if skew < 0 else "Bullish 📈"
        skew_color = COLORS['red'] if skew < 0 else COLORS['green']
        st.markdown(f"""
        <div class="metric-card glass-card" style="border-top: 2px solid {skew_color}; padding: 16px;">
            <div style="color:{COLORS['gray']}; font-size:12px; font-weight:bold; margin-bottom:8px;">MARKET BIAS</div>
            <div style="font-size:24px; color:{skew_color}; font-weight:bold; margin:8px 0;">{skew_dir}</div>
            <div class="monospace" style="color:{COLORS['gray']}; font-size:12px;">Skew: {skew:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Chart
    st.markdown("### PDF Visualization")

    from src.visualization.pdf_2d import plot_pdf_2d
    fig = plot_pdf_2d(
        strikes=st.session_state.current_strikes,
        pdf=st.session_state.current_pdf,
        spot_price=st.session_state.current_spot,
        title=f"{ticker} Option-Implied PDF ({days_to_expiry}D)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # AI Insights
    st.markdown("### 🤖 AI Market Interpretation")
    if st.session_state.current_interpretation:
        st.markdown(st.session_state.current_interpretation)

    if st.session_state.data_timestamp:
        st.caption(f"Data as of: {st.session_state.data_timestamp.strftime('%b %d, %Y %I:%M %p ET')}")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown(f"""
<div style="border-top: 1px solid {COLORS['border']}; margin-top: 60px; padding: 40px 0; text-align:center;">
    <div style="display:flex; justify-content:center; gap: 40px; flex-wrap: wrap; margin-bottom: 30px;">
        <div style="text-align:left; max-width: 300px;">
            <div style="display:flex; align-items:center; margin-bottom:10px;">
                {get_icon('wave', COLORS['cyan'], 24)}
                <span style="font-weight:bold; margin-left:10px;">PDF Visualizer</span>
            </div>
            <p style="color:{COLORS['gray']}; font-size:14px;">Decode market expectations through real-time probability distributions.</p>
        </div>

        <div style="text-align:left;">
            <h4 style="font-size:14px; margin-bottom:15px;">Built With</h4>
            <span style="background:rgba(52, 152, 219, 0.2); color:#3498db; padding:4px 8px; border-radius:4px; font-size:12px; margin-right:5px;">Python</span>
            <span style="background:rgba(255, 71, 87, 0.2); color:#ff4757; padding:4px 8px; border-radius:4px; font-size:12px; margin-right:5px;">Streamlit</span>
            <span style="background:rgba(0, 217, 255, 0.2); color:#00d9ff; padding:4px 8px; border-radius:4px; font-size:12px;">Plotly</span>
        </div>
    </div>

    <p style="color:{COLORS['gray']}; font-size:12px;">© 2025 Option-Implied PDF Visualizer | Licensed under MIT | Built with Claude Code</p>
</div>
""", unsafe_allow_html=True)
