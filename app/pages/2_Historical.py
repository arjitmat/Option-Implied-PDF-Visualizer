"""
Historical Page - Browse past PDF snapshots and patterns.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.state import init_session_state
from app.utils.helpers import load_custom_css, show_info, format_number, format_percentage, format_date
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Historical - PDF Visualizer", page_icon="📜", layout="wide")

init_session_state()
load_custom_css()
render_sidebar()

st.title("📜 Historical Analysis")
st.markdown("### Browse past PDF snapshots and pattern matches")

try:
    from src.database.history_api import get_history_api
    api = get_history_api()

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        days_back = st.slider("Days to look back", 1, 90, 30)
    with col2:
        ticker_filter = st.text_input("Filter by ticker", value="SPY").upper()

    # Get historical snapshots
    snapshots_list = api.get_pdf_history(ticker=ticker_filter, days=days_back)

    if snapshots_list:
        st.success(f"Found {len(snapshots_list)} snapshots")

        # Display as table
        st.markdown("### Recent Snapshots")

        for snapshot in snapshots_list[:20]:  # Show latest 20
            with st.expander(f"{snapshot['ticker']} - {format_date(datetime.fromisoformat(snapshot['timestamp']))} (DTE: {snapshot['days_to_expiry']})"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Spot Price", f"${format_number(snapshot['spot_price'])}")
                    st.metric("Expected Price", f"${format_number(snapshot['statistics'].get('mean', 0))}")

                with col2:
                    st.metric("Implied Move", f"±{format_number(snapshot['statistics'].get('implied_move_pct', 0), 2)}%")
                    st.metric("Skewness", format_number(snapshot['statistics'].get('skewness', 0), 3))

                with col3:
                    st.metric("DTE", f"{snapshot['days_to_expiry']} days")
                    st.metric("Model", snapshot.get('model_used', 'N/A'))

                if snapshot.get('interpretation'):
                    st.markdown("**Interpretation:**")
                    st.text(snapshot['interpretation'][:500] + "..." if len(snapshot['interpretation']) > 500 else snapshot['interpretation'])

                if st.button(f"Load #{snapshot['id']}", key=f"load_{snapshot['id']}"):
                    # Load this snapshot into current analysis
                    from app.utils.state import update_analysis_results
                    import numpy as np

                    update_analysis_results(
                        pdf=np.array(snapshot['pdf_values']),
                        strikes=np.array(snapshot['strikes']),
                        stats=snapshot['statistics'],
                        interpretation=snapshot.get('interpretation'),
                        spot=snapshot['spot_price'],
                        snapshot_id=snapshot['id']
                    )
                    st.success(f"Loaded snapshot #{snapshot['id']}")
                    st.switch_page("pages/1_Live_Analysis.py")

    else:
        show_info("No historical snapshots found. Run some analyses first!")

except Exception as e:
    st.error(f"Error loading historical data: {str(e)}")

st.markdown("---")
st.caption("Historical Analysis | Option-Implied PDF Visualizer")
