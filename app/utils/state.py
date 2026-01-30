"""
Session state management for Streamlit app.

Centralizes all session state initialization and management.
"""

import streamlit as st
from datetime import datetime


def init_session_state():
    """
    Initialize all session state variables.

    Call this at the start of every page to ensure state is initialized.
    """
    # Analysis settings
    if 'ticker' not in st.session_state:
        st.session_state.ticker = 'SPY'

    if 'days_to_expiry' not in st.session_state:
        st.session_state.days_to_expiry = 30

    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = 'standard'

    if 'use_sabr' not in st.session_state:
        st.session_state.use_sabr = True

    # Current analysis results
    if 'current_pdf' not in st.session_state:
        st.session_state.current_pdf = None

    if 'current_strikes' not in st.session_state:
        st.session_state.current_strikes = None

    if 'current_stats' not in st.session_state:
        st.session_state.current_stats = None

    if 'current_interpretation' not in st.session_state:
        st.session_state.current_interpretation = None

    if 'current_spot' not in st.session_state:
        st.session_state.current_spot = None

    if 'current_snapshot_id' not in st.session_state:
        st.session_state.current_snapshot_id = None

    # Historical pattern matches
    if 'pattern_matches' not in st.session_state:
        st.session_state.pattern_matches = []

    # Predictions
    if 'pending_predictions' not in st.session_state:
        st.session_state.pending_predictions = []

    # UI state
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False

    if 'auto_save' not in st.session_state:
        st.session_state.auto_save = True

    # Cache settings
    if 'cache_duration' not in st.session_state:
        st.session_state.cache_duration = 900  # 15 minutes

    # Error tracking
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None

    if 'error_timestamp' not in st.session_state:
        st.session_state.error_timestamp = None


def clear_analysis_state():
    """Clear current analysis results (for re-running analysis)."""
    st.session_state.current_pdf = None
    st.session_state.current_strikes = None
    st.session_state.current_stats = None
    st.session_state.current_interpretation = None
    st.session_state.current_spot = None
    st.session_state.current_snapshot_id = None
    st.session_state.pattern_matches = []


def set_error(error_msg: str):
    """Record an error in session state."""
    st.session_state.last_error = error_msg
    st.session_state.error_timestamp = datetime.now()


def clear_error():
    """Clear error state."""
    st.session_state.last_error = None
    st.session_state.error_timestamp = None


def has_current_analysis() -> bool:
    """Check if there's a current analysis loaded."""
    return (
        st.session_state.current_pdf is not None and
        st.session_state.current_strikes is not None and
        st.session_state.current_stats is not None
    )


def get_analysis_params() -> dict:
    """Get current analysis parameters."""
    return {
        'ticker': st.session_state.ticker,
        'days_to_expiry': st.session_state.days_to_expiry,
        'analysis_mode': st.session_state.analysis_mode,
        'use_sabr': st.session_state.use_sabr
    }


def update_analysis_results(
    pdf,
    strikes,
    stats,
    interpretation,
    spot,
    snapshot_id=None,
    pattern_matches=None
):
    """
    Update session state with new analysis results.

    Args:
        pdf: PDF values array
        strikes: Strike prices array
        stats: Statistics dictionary
        interpretation: AI interpretation text
        spot: Spot price
        snapshot_id: Database snapshot ID (optional)
        pattern_matches: List of pattern matches (optional)
    """
    st.session_state.current_pdf = pdf
    st.session_state.current_strikes = strikes
    st.session_state.current_stats = stats
    st.session_state.current_interpretation = interpretation
    st.session_state.current_spot = spot
    st.session_state.current_snapshot_id = snapshot_id

    if pattern_matches is not None:
        st.session_state.pattern_matches = pattern_matches
