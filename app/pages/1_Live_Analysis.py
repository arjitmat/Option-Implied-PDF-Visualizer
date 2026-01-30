"""
Live Analysis Page - Real-time PDF extraction and visualization.
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.state import init_session_state, update_analysis_results, set_error, clear_error
from app.utils.helpers import (
    load_custom_css, show_success, show_error, show_info, show_warning,
    format_number, format_percentage, format_statistics_table
)
from app.components.sidebar import render_sidebar

# Page config
st.set_page_config(
    page_title="Live Analysis - PDF Visualizer",
    page_icon="🔴",
    layout="wide"
)

# Initialize
init_session_state()
load_custom_css()

# Render sidebar and get settings
sidebar_action = render_sidebar()

# Main content
st.title("🔴 Live Analysis")
st.markdown("### Real-time option-implied probability distribution extraction")

# Check if analyze button was clicked
if sidebar_action and sidebar_action.get('action') == 'analyze':
    st.session_state.run_analysis = True

# Analyze button in main area
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    st.markdown(f"**Ticker**: {st.session_state.ticker} | **DTE**: {st.session_state.days_to_expiry} days")
with col2:
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        st.session_state.run_analysis = True
with col3:
    if st.button("💾 Save to DB", use_container_width=True, disabled=not st.session_state.current_pdf):
        st.session_state.save_to_db = True
with col4:
    if st.button("🔄 Clear", use_container_width=True):
        from app.utils.state import clear_analysis_state
        clear_analysis_state()
        st.rerun()

st.markdown("---")

# Run analysis if requested
if st.session_state.get('run_analysis', False):
    st.session_state.run_analysis = False

    with st.spinner("⏳ Running analysis..."):
        try:
            clear_error()

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Step 1: Fetch data
            status_text.text("Step 1/6: Fetching option chain data...")
            progress_bar.progress(0.1)

            from src.data.data_manager import DataManager
            data_manager = DataManager()

            options_df = data_manager.get_options(
                ticker=st.session_state.ticker,
                min_expiry_days=st.session_state.days_to_expiry - 3,
                max_expiry_days=st.session_state.days_to_expiry + 3
            )

            if options_df is None or options_df.empty:
                show_error("Failed to fetch option data. Please check ticker and try again.")
                st.stop()

            # Step 2: Get risk-free rate
            status_text.text("Step 2/6: Fetching risk-free rate...")
            progress_bar.progress(0.2)

            risk_free_rate = data_manager.get_risk_free_rate()

            # Get spot price (try multiple methods)
            if 'underlying_price' in options_df.columns:
                spot_price = options_df['underlying_price'].iloc[0]
            else:
                # Fetch directly from data manager
                try:
                    spot_price = data_manager.get_spot_price(st.session_state.ticker)
                except:
                    # Final fallback: estimate from ATM strike
                    spot_price = options_df['strike'].median()

            # Step 3: Calculate PDF
            status_text.text("Step 3/6: Calculating probability distribution...")
            progress_bar.progress(0.4)

            from src.core.breeden_litz import BreedenlitzenbergPDF

            # Initialize PDF calculator (no parameters)
            pdf_calculator = BreedenlitzenbergPDF()

            # Standardize column names (handle both snake_case and camelCase)
            column_mapping = {}
            if 'option_type' in options_df.columns:
                column_mapping['option_type'] = 'optionType'
            if 'implied_volatility' in options_df.columns:
                column_mapping['implied_volatility'] = 'impliedVolatility'
            if column_mapping:
                options_df = options_df.rename(columns=column_mapping)

            # Filter for calls
            calls = options_df[options_df['optionType'] == 'call'].copy()

            if calls.empty:
                show_error("No call options found in data")
                st.stop()

            # Calculate time to expiry in years
            exp_date = calls['expiration'].iloc[0]
            # Convert string to datetime if needed
            if isinstance(exp_date, str):
                exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
            days_to_exp = (exp_date - datetime.now()).days
            T = days_to_exp / 365.0

            # Prepare DataFrame with required columns for calculate_from_options
            pdf_input_df = calls[['strike', 'impliedVolatility']].copy()

            # Add price column (mid price if available, otherwise use lastPrice)
            if 'bid' in calls.columns and 'ask' in calls.columns:
                pdf_input_df['price'] = (calls['bid'] + calls['ask']) / 2
            elif 'lastPrice' in calls.columns:
                pdf_input_df['price'] = calls['lastPrice']
            elif 'last' in calls.columns:
                pdf_input_df['price'] = calls['last']
            else:
                # Fallback: use Black-Scholes theoretical price
                show_warning("No price data available, using theoretical prices")
                from scipy.stats import norm
                sigma = pdf_input_df['impliedVolatility'].values
                K = pdf_input_df['strike'].values
                d1 = (np.log(spot_price / K) + (risk_free_rate + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
                d2 = d1 - sigma * np.sqrt(T)
                pdf_input_df['price'] = spot_price * norm.cdf(d1) - K * np.exp(-risk_free_rate * T) * norm.cdf(d2)

            # Calculate PDF using correct method
            interpolation_method = 'sabr' if st.session_state.use_sabr else 'spline'
            pdf_strikes, pdf_values = pdf_calculator.calculate_from_options(
                options_df=pdf_input_df,
                spot_price=spot_price,
                risk_free_rate=risk_free_rate,
                time_to_expiry=T,
                option_type='call',
                interpolation_method=interpolation_method
            )

            # Step 4: Calculate statistics
            status_text.text("Step 4/6: Calculating statistics...")
            progress_bar.progress(0.6)

            from src.core.statistics import PDFStatistics

            # PDFStatistics constructor: (strikes, pdf, spot_price, time_to_expiry)
            stats_calculator = PDFStatistics(
                strikes=pdf_strikes,
                pdf=pdf_values,
                spot_price=spot_price,
                time_to_expiry=T  # Use T (years), not days_to_exp
            )
            statistics = stats_calculator.get_summary()  # Returns Dict[str, float]

            # Step 5: Find patterns (if DB has data)
            status_text.text("Step 5/6: Finding similar patterns...")
            progress_bar.progress(0.75)

            # Initialize API for pattern matching AND auto-save
            pattern_matches = []
            api = None
            try:
                from src.database.history_api import get_history_api
                api = get_history_api()

                if api.get_stats()['total_snapshots'] > 0:
                    pattern_matches = api.find_similar_patterns(
                        current_pdf=pdf_values,
                        current_strikes=pdf_strikes,
                        current_stats=statistics,
                        ticker=st.session_state.ticker,
                        n_results=5,
                        min_similarity=0.7
                    )
            except Exception as e:
                st.warning(f"Pattern matching unavailable: {str(e)}")

            # Step 6: Generate interpretation
            status_text.text("Step 6/6: Generating AI interpretation...")
            progress_bar.progress(0.9)

            from src.ai.interpreter import PDFInterpreter

            interpreter = PDFInterpreter(mode=st.session_state.analysis_mode)
            interp_result = interpreter.interpret_single_pdf(
                ticker=st.session_state.ticker,
                spot=spot_price,
                stats=statistics,
                days_to_expiry=days_to_exp,
                historical_matches=pattern_matches if pattern_matches else None
            )

            interpretation = interp_result['interpretation']
            model_used = interp_result['model']

            # Complete
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")

            # Update session state
            update_analysis_results(
                pdf=pdf_values,
                strikes=pdf_strikes,
                stats=statistics,
                interpretation=interpretation,
                spot=spot_price,
                pattern_matches=pattern_matches
            )

            # Auto-save if enabled
            if st.session_state.auto_save and api is not None:
                try:
                    snapshot_id = api.save_pdf_analysis(
                        ticker=st.session_state.ticker,
                        spot_price=spot_price,
                        days_to_expiry=days_to_exp,
                        expiration_date=exp_date,
                        risk_free_rate=risk_free_rate,
                        strikes=pdf_strikes,
                        pdf_values=pdf_values,
                        statistics=statistics,
                        sabr_params=None,  # No longer returned by calculate_from_options
                        interpolation_method=interpolation_method,
                        interpretation=interpretation,
                        interpretation_mode=st.session_state.analysis_mode,
                        model_used=model_used,
                        store_in_vector_db=True
                    )

                    st.session_state.current_snapshot_id = snapshot_id

                    # Store pattern matches
                    if pattern_matches:
                        api.save_pattern_matches(snapshot_id, pattern_matches)

                    show_success(f"Analysis saved to database (ID: {snapshot_id})")
                except Exception as e:
                    show_warning(f"Auto-save failed: {str(e)}")

        except Exception as e:
            show_error(f"Analysis failed: {str(e)}")
            set_error(str(e))
            import traceback
            st.code(traceback.format_exc())

# Display results if available
if st.session_state.current_pdf is not None:
    st.markdown("## 📊 Results")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Spot Price",
            f"${format_number(st.session_state.current_spot)}",
            help="Current underlying price"
        )

    with col2:
        mean = st.session_state.current_stats.get('mean', 0)
        delta = mean - st.session_state.current_spot
        st.metric(
            "Expected Price",
            f"${format_number(mean)}",
            delta=f"${format_number(delta, 2)}",
            help="Risk-neutral mean"
        )

    with col3:
        impl_move = st.session_state.current_stats.get('implied_move_pct', 0)
        st.metric(
            "Implied Move",
            f"±{format_number(impl_move, 2)}%",
            help="Expected price range"
        )

    with col4:
        skew = st.session_state.current_stats.get('skewness', 0)
        skew_dir = "📉 Bearish" if skew < 0 else "📈 Bullish"
        st.metric(
            "Bias",
            skew_dir,
            delta=f"{format_number(skew, 3)}",
            help="Distribution skewness"
        )

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizations", "📊 Statistics", "🤖 AI Interpretation", "🔍 Patterns"])

    with tab1:
        st.markdown("### Probability Distribution")

        # Plot 2D PDF
        from src.visualization.pdf_2d import plot_pdf_2d

        fig_2d = plot_pdf_2d(
            strikes=st.session_state.current_strikes,
            pdf=st.session_state.current_pdf,
            spot_price=st.session_state.current_spot,
            title=f"{st.session_state.ticker} Option-Implied PDF ({st.session_state.days_to_expiry}D)"
        )

        st.plotly_chart(fig_2d, use_container_width=True)

        # Probability table
        st.markdown("### Key Probabilities")

        from src.visualization.probability_table import create_strikes_table
        try:
            from scipy.integrate import cumulative_trapezoid
        except ImportError:
            from scipy.integrate import cumtrapz as cumulative_trapezoid

        # Calculate CDF for the table
        cdf = cumulative_trapezoid(st.session_state.current_pdf, st.session_state.current_strikes, initial=0)
        cdf = cdf / cdf[-1]  # Normalize

        prob_table = create_strikes_table(
            strikes=st.session_state.current_strikes,
            probabilities=cdf,
            spot_price=st.session_state.current_spot,
            num_strikes=10
        )

        st.plotly_chart(prob_table, use_container_width=True)

    with tab2:
        st.markdown("### Statistical Summary")

        # Display stats table
        stats_html = format_statistics_table(st.session_state.current_stats)
        st.markdown(stats_html, unsafe_allow_html=True)

        # Additional insights
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Distribution Shape")
            st.write(f"**Skewness**: {format_number(st.session_state.current_stats.get('skewness', 0), 3)}")
            st.write(f"**Kurtosis**: {format_number(st.session_state.current_stats.get('excess_kurtosis', 0), 3)}")

            skew = st.session_state.current_stats.get('skewness', 0)
            if skew < -0.2:
                st.info("Strong bearish tilt - elevated downside risk")
            elif skew > 0.2:
                st.info("Strong bullish tilt - elevated upside potential")
            else:
                st.info("Relatively symmetric distribution")

        with col2:
            st.markdown("#### 📉 Tail Risk")
            st.write(f"**Prob(+10%)**: {format_percentage(st.session_state.current_stats.get('prob_up_10pct', 0))}")
            st.write(f"**Prob(-10%)**: {format_percentage(st.session_state.current_stats.get('prob_down_10pct', 0))}")

            tail_ratio = st.session_state.current_stats.get('prob_down_10pct', 0) / max(st.session_state.current_stats.get('prob_up_10pct', 0), 0.01)
            if tail_ratio > 1.2:
                st.warning("Elevated downside tail risk")
            elif tail_ratio < 0.8:
                st.info("Elevated upside tail potential")

    with tab3:
        st.markdown("### 🤖 AI Interpretation")

        if st.session_state.current_interpretation:
            st.markdown(st.session_state.current_interpretation)
        else:
            st.info("No interpretation available")

        st.caption(f"Mode: {st.session_state.analysis_mode}")

    with tab4:
        st.markdown("### 🔍 Historical Pattern Matches")

        if st.session_state.pattern_matches:
            st.success(f"Found {len(st.session_state.pattern_matches)} similar patterns")

            for i, match in enumerate(st.session_state.pattern_matches, 1):
                with st.expander(f"Match #{i}: {match.get('date', 'Unknown')} (Similarity: {format_percentage(match.get('similarity', 0))})"):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.metric("Similarity", format_percentage(match.get('similarity', 0)))
                        st.metric("Date", match.get('date', 'N/A'))
                        st.metric("DTE", f"{match.get('dte', 'N/A')} days")

                    with col2:
                        if match.get('description'):
                            st.markdown("**Description:**")
                            st.write(match['description'])
                        else:
                            st.caption("No description available")
        else:
            st.info("No similar patterns found. Database may be empty or no matches above similarity threshold.")

else:
    # No analysis yet
    show_info("""
    **Click "Run Analysis" to start**

    This will:
    1. Fetch option chain data for {ticker}
    2. Calculate risk-neutral probability distribution
    3. Compute statistics (mean, vol, skew, tail probs)
    4. Find similar historical patterns
    5. Generate AI interpretation

    The entire process takes 10-30 seconds depending on data availability.
    """.format(ticker=st.session_state.ticker))

# Footer
st.markdown("---")
st.caption("Live Analysis | Option-Implied PDF Visualizer")
