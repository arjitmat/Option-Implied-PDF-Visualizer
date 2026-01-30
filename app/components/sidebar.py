"""
Shared sidebar component for all pages.
"""

import streamlit as st
from app.utils.helpers import validate_ticker, get_analysis_mode_description


def render_sidebar():
    """
    Render the shared sidebar with analysis controls.

    Returns:
        Dictionary with selected parameters
    """
    with st.sidebar:
        st.markdown("## ⚙️ Analysis Settings")

        # Ticker selection
        ticker = st.text_input(
            "Ticker Symbol",
            value=st.session_state.ticker,
            max_chars=5,
            help="Enter stock ticker (e.g., SPY, QQQ)"
        ).upper()

        if ticker != st.session_state.ticker:
            if validate_ticker(ticker):
                st.session_state.ticker = ticker
            else:
                st.warning("Invalid ticker symbol")

        # Days to expiry
        days_to_expiry = st.selectbox(
            "Days to Expiration",
            options=[7, 14, 21, 30, 45, 60, 90],
            index=3,  # Default to 30
            help="Select target expiration"
        )
        st.session_state.days_to_expiry = days_to_expiry

        # Analysis mode
        analysis_mode = st.selectbox(
            "Analysis Mode",
            options=['standard', 'conservative', 'aggressive', 'educational'],
            index=0,
            help="Select AI interpretation style"
        )
        st.session_state.analysis_mode = analysis_mode

        st.caption(get_analysis_mode_description(analysis_mode))

        st.markdown("---")

        # Advanced settings (collapsible)
        with st.expander("🔧 Advanced Settings"):
            use_sabr = st.checkbox(
                "Use SABR Model",
                value=st.session_state.use_sabr,
                help="Use SABR for IV interpolation (recommended)"
            )
            st.session_state.use_sabr = use_sabr

            auto_save = st.checkbox(
                "Auto-save to Database",
                value=st.session_state.auto_save,
                help="Automatically save analyses to database"
            )
            st.session_state.auto_save = auto_save

            cache_duration = st.slider(
                "Cache Duration (minutes)",
                min_value=5,
                max_value=60,
                value=15,
                step=5,
                help="How long to cache data"
            )
            st.session_state.cache_duration = cache_duration * 60

        st.markdown("---")

        # Quick actions
        st.markdown("### 🚀 Quick Actions")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Analyze", use_container_width=True):
                return {'action': 'analyze'}
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                return {'action': 'refresh'}

        st.markdown("---")

        # Current analysis summary
        if st.session_state.current_spot is not None:
            st.markdown("### 📈 Current Analysis")
            st.metric("Ticker", st.session_state.ticker)
            st.metric("Spot Price", f"${st.session_state.current_spot:.2f}")

            if st.session_state.current_stats:
                stats = st.session_state.current_stats
                st.metric(
                    "Expected Price",
                    f"${stats.get('mean', 0):.2f}",
                    delta=f"{stats.get('mean', 0) - st.session_state.current_spot:.2f}"
                )
                st.metric(
                    "Implied Move",
                    f"±{stats.get('implied_move_pct', 0):.2f}%"
                )

        st.markdown("---")

        # Database stats
        st.markdown("### 💾 Database Stats")
        try:
            from src.database.history_api import get_history_api
            api = get_history_api()
            db_stats = api.get_stats()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Snapshots", db_stats.get('total_snapshots', 0))
            with col2:
                st.metric("Predictions", db_stats.get('total_predictions', 0))

            if db_stats.get('first_snapshot_date'):
                st.caption(f"First: {db_stats['first_snapshot_date'].strftime('%Y-%m-%d')}")
            if db_stats.get('last_snapshot_date'):
                st.caption(f"Latest: {db_stats['last_snapshot_date'].strftime('%Y-%m-%d')}")

        except Exception as e:
            st.caption("Database not initialized")

        st.markdown("---")

        # Info
        st.caption("Built with Claude Code")
        st.caption("v1.0.0 | 2025-12-01")

    # Return current settings
    return {
        'ticker': st.session_state.ticker,
        'days_to_expiry': st.session_state.days_to_expiry,
        'analysis_mode': st.session_state.analysis_mode,
        'use_sabr': st.session_state.use_sabr,
        'auto_save': st.session_state.auto_save
    }
