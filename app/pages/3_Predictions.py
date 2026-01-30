"""
Predictions Page - Create and track prediction accuracy.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.state import init_session_state
from app.utils.helpers import load_custom_css, show_success, show_info, format_number, format_percentage, format_date
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Predictions - PDF Visualizer", page_icon="🎯", layout="wide")

init_session_state()
load_custom_css()
render_sidebar()

st.title("🎯 Prediction Tracking")
st.markdown("### Monitor accuracy of option-implied forecasts")

try:
    from src.database.history_api import get_history_api
    api = get_history_api()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📝 Create Prediction", "⏳ Pending", "✅ Evaluated"])

    with tab1:
        st.markdown("### Create New Prediction")

        if st.session_state.current_snapshot_id:
            st.info(f"Using current snapshot ID: {st.session_state.current_snapshot_id}")

            col1, col2 = st.columns(2)

            with col1:
                target_days = st.number_input("Days until target date", min_value=1, max_value=365, value=30)
                target_date = datetime.now() + timedelta(days=target_days)
                st.write(f"Target date: {target_date.strftime('%Y-%m-%d')}")

                condition = st.selectbox("Condition", ["above", "below", "between"])

            with col2:
                target_level = st.number_input(
                    "Target price level",
                    min_value=1.0,
                    value=float(st.session_state.current_spot) * 1.05 if st.session_state.current_spot else 100.0
                )

                if condition == "between":
                    target_upper = st.number_input("Upper level", min_value=target_level, value=target_level * 1.1)
                else:
                    target_upper = None

            # Calculate probability from current PDF
            if st.session_state.current_pdf is not None:
                from src.core.statistics import PDFStatistics
                stats_calc = PDFStatistics(st.session_state.current_strikes, st.session_state.current_pdf)

                if condition == "above":
                    prob = stats_calc.prob_above(target_level)
                elif condition == "below":
                    prob = stats_calc.prob_below(target_level)
                else:
                    prob = stats_calc.prob_between(target_level, target_upper)

                st.metric("Predicted Probability", format_percentage(prob))
                pred_prob = prob
            else:
                pred_prob = st.slider("Predicted Probability", 0.0, 1.0, 0.5, 0.01)

            notes = st.text_area("Notes (optional)", "")

            if st.button("💾 Create Prediction", type="primary"):
                try:
                    pred_id = api.create_prediction(
                        snapshot_id=st.session_state.current_snapshot_id,
                        target_date=target_date,
                        ticker=st.session_state.ticker,
                        condition=condition,
                        target_level=target_level,
                        predicted_probability=pred_prob,
                        target_level_upper=target_upper,
                        notes=notes
                    )
                    show_success(f"Prediction created! ID: {pred_id}")
                except Exception as e:
                    st.error(f"Failed to create prediction: {str(e)}")
        else:
            show_info("Run an analysis first to create a prediction")

    with tab2:
        st.markdown("### Pending Predictions")

        pending = api.get_pending_predictions()

        if pending:
            st.write(f"Found {len(pending)} pending predictions")

            for pred in pending:
                with st.expander(f"{pred['ticker']} {pred['condition']} ${format_number(pred['target_level'])} - {format_date(datetime.fromisoformat(pred['target_date']))}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Predicted Prob", format_percentage(pred['predicted_probability']))
                        st.write(f"**Forecast Date**: {format_date(datetime.fromisoformat(pred['forecast_date']))}")

                    with col2:
                        st.write(f"**Target Date**: {format_date(datetime.fromisoformat(pred['target_date']))}")
                        st.write(f"**Condition**: {pred['condition']}")

                    with col3:
                        st.write(f"**Target Level**: ${format_number(pred['target_level'])}")
                        if pred.get('notes'):
                            st.caption(pred['notes'])

                    # Evaluate button if target date passed
                    if datetime.fromisoformat(pred['target_date']) <= datetime.now():
                        actual_price = st.number_input(f"Actual price for #{pred['id']}", key=f"price_{pred['id']}")
                        if st.button(f"✅ Evaluate #{pred['id']}", key=f"eval_{pred['id']}"):
                            try:
                                result = api.evaluate_prediction(pred['id'], actual_price)
                                outcome = "✅ Condition MET" if result['actual_outcome'] else "❌ Condition NOT MET"
                                show_success(f"{outcome} | Brier Score: {format_number(result['accuracy_score'], 4)}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Evaluation failed: {str(e)}")
        else:
            show_info("No pending predictions")

    with tab3:
        st.markdown("### Evaluated Predictions")

        accuracy_stats = api.get_prediction_accuracy(ticker=st.session_state.ticker, days=90)

        if accuracy_stats['total_predictions'] > 0:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Evaluated", accuracy_stats['total_predictions'])
            with col2:
                st.metric("Correct", accuracy_stats['correct_predictions'])
            with col3:
                st.metric("Accuracy Rate", format_percentage(accuracy_stats['accuracy_rate']))

            if accuracy_stats.get('mean_brier_score'):
                st.metric("Mean Brier Score", format_number(accuracy_stats['mean_brier_score'], 4),
                         help="Lower is better (0 = perfect)")

            # Show individual predictions
            st.markdown("### Individual Predictions")
            for pred in accuracy_stats['predictions']:
                outcome_icon = "✅" if pred['actual_outcome'] else "❌"
                with st.expander(f"{outcome_icon} {pred['ticker']} - {format_date(datetime.fromisoformat(pred['target_date']))}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Predicted**: {format_percentage(pred['predicted_probability'])}")
                        st.write(f"**Condition**: {pred['condition']} ${format_number(pred['target_level'])}")
                    with col2:
                        st.write(f"**Actual Price**: ${format_number(pred['actual_price'])}")
                        st.write(f"**Brier Score**: {format_number(pred['accuracy_score'], 4)}")
        else:
            show_info("No evaluated predictions yet")

except Exception as e:
    st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Prediction Tracking | Option-Implied PDF Visualizer")
