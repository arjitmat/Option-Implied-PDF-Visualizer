"""
Option-Implied PDF Visualizer - Main Streamlit App

Extracts and visualizes risk-neutral probability distributions from option markets
using the Breeden-Litzenberger formula.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.state import init_session_state
from app.utils.helpers import load_custom_css


# Page config
st.set_page_config(
    page_title="Option-Implied PDF Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Load custom CSS
load_custom_css()

# Main page content
st.title("📊 Option-Implied PDF Visualizer")
st.markdown("### Extract market expectations from option prices")

st.markdown("""
---

Welcome to the **Option-Implied PDF Visualizer**! This tool extracts risk-neutral probability
distributions from SPY/SPX option markets using the Breeden-Litzenberger formula.

## 🎯 What Does This Do?

Options markets contain valuable information about where traders expect prices to move.
This tool extracts that hidden information and presents it as:

- **3D Probability Surfaces** - Visualize how probabilities change across strikes and time
- **Statistical Analysis** - Mean, volatility, skewness, tail probabilities
- **AI Interpretation** - Plain English explanations of what the PDFs mean
- **Historical Patterns** - Find similar past market conditions
- **Prediction Tracking** - Monitor accuracy of option-implied forecasts

## 🚀 Quick Start

1. **Live Analysis** - Analyze current market PDFs in real-time
2. **Historical** - Browse past PDFs and pattern matches
3. **Predictions** - Track forecast accuracy over time
4. **About** - Learn how it works

## 📈 How It Works

The tool uses the **Breeden-Litzenberger formula** to extract probability densities:

```
f(K) = e^(rT) × ∂²C/∂K²
```

Where:
- `f(K)` = probability density at strike K
- `C` = call option price
- `r` = risk-free rate
- `T` = time to expiration

This gives us the full probability distribution that the market is pricing in.

## 🔑 Key Features

### Data Sources
- **OpenBB Terminal** (primary option chain data)
- **Yahoo Finance** (backup data source)
- **FRED API** (risk-free rates)

### Mathematical Models
- **SABR Volatility Model** - Smooth IV interpolation
- **Breeden-Litzenberger** - PDF extraction
- **Pattern Matching** - Cosine similarity + statistical features

### AI Interpretation
- **Local LLM** (Ollama + Qwen3-7B)
- **4 Analysis Modes** - Standard, Conservative, Aggressive, Educational
- **Intelligent Fallback** - Works without AI if needed

### Database
- **SQLite** - Historical snapshot storage
- **ChromaDB** - Fast vector similarity search
- **Prediction Tracking** - Brier score accuracy

## 📊 Example Analysis

A typical PDF analysis includes:

**Market Expectations**
- Expected price (mean): $450.50
- Volatility (std): $15.20
- Implied move: ±3.38%

**Directional Bias**
- Skewness: -0.15 (slight bearish tilt)
- Excess kurtosis: 0.50 (moderate fat tails)

**Tail Probabilities**
- Prob(+5% move): 22%
- Prob(-5% move): 18%
- Prob(+10% move): 10%
- Prob(-10% move): 8%

**AI Interpretation**
> "Market is pricing in moderate uncertainty with a slight downside bias. The negative
> skewness suggests elevated demand for downside protection. This pattern is similar to
> pre-Fed announcement periods in October 2023."

## 🎨 Navigation

Use the sidebar to navigate between pages:

- **🔴 Live Analysis** - Real-time PDF extraction and visualization
- **📜 Historical** - Browse historical PDFs and find similar patterns
- **🎯 Predictions** - Create and track prediction accuracy
- **ℹ️ About** - Documentation and technical details

## ⚙️ Configuration

### API Keys Required
- **FRED API Key** (free) - For risk-free rates
  - Get it here: https://fred.stlouisfed.org/docs/api/api_key.html

### Optional Setup
- **Ollama** (for AI interpretation)
  - Install from: https://ollama.ai/download
  - System works with rule-based fallback if not installed

## 📚 Learn More

- **Source Code**: Built with Python, Streamlit, Plotly
- **Algorithm**: Breeden & Litzenberger (1978)
- **AI**: Local LLM (privacy-focused)
- **License**: MIT

---

**Ready to get started?** Use the sidebar to navigate to **Live Analysis** →

""")

# Sidebar info
with st.sidebar:
    st.markdown("### 👋 Welcome!")
    st.markdown("""
    This is the **home page**. Use the navigation above to:

    - 🔴 **Live Analysis** - Analyze current markets
    - 📜 **Historical** - Browse past PDFs
    - 🎯 **Predictions** - Track accuracy
    - ℹ️ **About** - Learn more
    """)

    st.markdown("---")

    st.markdown("### 📊 Quick Stats")

    # Get database stats
    try:
        from src.database.history_api import get_history_api
        api = get_history_api()
        stats = api.get_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Snapshots", stats.get('total_snapshots', 0))
        with col2:
            st.metric("Predictions", stats.get('total_predictions', 0))
    except Exception as e:
        st.caption("Database not yet initialized")

    st.markdown("---")
    st.caption("Built with Claude Code")
    st.caption("Last updated: 2025-12-01")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Option-Implied PDF Visualizer | Built with Streamlit & Claude Code</p>
    <p style='font-size: 0.8em;'>
        Data: OpenBB, Yahoo Finance, FRED | AI: Ollama + Qwen3-7B
    </p>
</div>
""", unsafe_allow_html=True)
