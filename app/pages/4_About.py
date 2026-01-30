"""
About Page - Documentation and technical details.
"""

import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.state import init_session_state
from app.utils.helpers import load_custom_css

st.set_page_config(page_title="About - PDF Visualizer", page_icon="ℹ️", layout="wide")

init_session_state()
load_custom_css()

st.title("ℹ️ About This Tool")
st.markdown("### Technical documentation and how it works")

tab1, tab2, tab3, tab4 = st.tabs(["📚 Overview", "🔬 Algorithm", "⚙️ Tech Stack", "📖 Usage Guide"])

with tab1:
    st.markdown("""
## What is This?

The **Option-Implied PDF Visualizer** extracts risk-neutral probability distributions from option markets
using the Breeden-Litzenberger formula. It shows where the market expects prices to move.

### Key Features

- **3D Probability Surfaces** - Visualize probabilities across strikes and time
- **Statistical Analysis** - Mean, volatility, skewness, tail probabilities
- **AI Interpretation** - Plain English explanations
- **Historical Patterns** - Find similar past market conditions
- **Prediction Tracking** - Monitor forecast accuracy

### Why Use This?

**For Traders:**
- Understand market expectations beyond implied volatility
- Quantify tail risk and directional bias
- Compare current vs historical distributions

**For Risk Managers:**
- Extract full probability distributions from market prices
- Measure tail risk quantitatively
- Track prediction accuracy over time

**For Researchers:**
- Study evolution of market expectations
- Analyze pattern similarity
- Research option-implied forecasting

### How It Works (Simple)

1. Fetch option chain data from market
2. Interpolate implied volatility surface (SABR model)
3. Calculate call prices across strikes
4. Apply Breeden-Litzenberger formula to extract PDF
5. Calculate statistics from PDF
6. Find similar historical patterns
7. Generate AI interpretation

The entire process takes 10-30 seconds.
    """)

with tab2:
    st.markdown("""
## The Algorithm

### Breeden-Litzenberger Formula

The tool uses the **Breeden-Litzenberger (1978)** formula to extract risk-neutral probability densities:

```
f(K) = e^(rT) × ∂²C/∂K²
```

Where:
- `f(K)` = probability density at strike K
- `C` = call option price as function of strike
- `r` = risk-free rate
- `T` = time to expiration
- `e^(rT)` = discount factor

### Why This Works

The price of a European call can be expressed as:

```
C(K) = e^(-rT) × ∫[K to ∞] (S - K) × f(S) dS
```

Taking derivatives:
1. First derivative: `∂C/∂K = -e^(-rT) × P(S > K)`
2. Second derivative: `∂²C/∂K² = e^(-rT) × f(K)`

Rearranging gives us the PDF!

### Implementation Steps

**Step 1: SABR Calibration**
- Calibrate SABR model to market IV smile
- Parameters: α (vol-of-vol), ρ (correlation), ν (elasticity)
- Fallback to cubic spline if SABR fails

**Step 2: IV Interpolation**
- Create dense strike grid (200+ points)
- Interpolate IV using calibrated SABR
- Handle extrapolation beyond market strikes

**Step 3: Call Price Calculation**
- Use Black-Scholes with interpolated IV
- Calculate prices across dense strike grid

**Step 4: Numerical Differentiation**
- Compute second derivative: ∂²C/∂K²
- Apply Savitzky-Golay smoothing
- Enforce non-negativity

**Step 5: Normalization**
- Multiply by e^(rT)
- Ensure PDF integrates to 1.0
- Validate probability properties

### Statistical Measures

From the PDF, we calculate:
- **Mean**: Expected price (first moment)
- **Variance**: Price uncertainty (second moment)
- **Skewness**: Directional bias (third moment)
- **Kurtosis**: Tail fatness (fourth moment)
- **Tail Probabilities**: P(move > X%)
- **Confidence Intervals**: 68%, 95%, 99%

### Pattern Matching

We find similar historical PDFs using:
- **Cosine Similarity**: Shape comparison
- **Statistical Features**: Skew, kurtosis, implied move
- **Combined Score**: 70% shape + 30% stats
    """)

with tab3:
    st.markdown("""
## Tech Stack

### Backend

**Python 3.11+**
- NumPy - Numerical computation
- SciPy - Optimization, interpolation
- Pandas - Data manipulation

### Data Sources

**OpenBB Terminal** (Primary)
- Free, no API key required
- Comprehensive option chain data

**Yahoo Finance** (Backup)
- Free, no API key required
- Automatic fallback if OpenBB fails

**FRED API** (Risk-Free Rate)
- Free API key required
- Get it here: https://fred.stlouisfed.org/docs/api/api_key.html

### Mathematical Models

**SABR Volatility Model**
- Industry-standard for equity options
- Captures smile/skew dynamics
- Fallback to cubic spline

**Breeden-Litzenberger**
- Extract PDF from option prices
- Numerical differentiation with smoothing
- Non-negativity constraints

### AI Interpretation

**Ollama + Qwen3-7B**
- Local LLM (privacy-focused)
- 4 analysis modes
- Intelligent fallback if unavailable

### Database

**SQLite**
- Embedded database
- 3 tables: PDFSnapshot, Prediction, PatternMatch
- SQLAlchemy ORM

**ChromaDB** (Optional)
- Vector similarity search
- 10-100x faster pattern matching
- Graceful fallback to SQLite-only

### Visualization

**Plotly**
- Interactive 3D surfaces
- 2D PDF plots
- Probability tables
- Dark theme styling

### Frontend

**Streamlit**
- Python-native web framework
- Multi-page app
- Real-time updates
- Built-in caching

### Deployment

**Docker**
- Containerized deployment
- HuggingFace Spaces ready
- Environment variable configuration
    """)

with tab4:
    st.markdown("""
## Usage Guide

### Quick Start

1. **Navigate to Live Analysis**
   - Click "🔴 Live Analysis" in sidebar

2. **Select Parameters**
   - Ticker: SPY, QQQ, etc.
   - Days to Expiry: 7-90 days
   - Analysis Mode: Standard/Conservative/Aggressive/Educational

3. **Run Analysis**
   - Click "🚀 Run Analysis"
   - Wait 10-30 seconds

4. **Explore Results**
   - View PDF visualization
   - Check statistics
   - Read AI interpretation
   - Find similar patterns

### Advanced Features

**Auto-Save**
- Enable in sidebar → Advanced Settings
- Automatically saves analyses to database
- Stores pattern matches

**SABR Model**
- Default: Enabled (recommended)
- Disable to use cubic spline fallback
- SABR generally provides better results

**Analysis Modes**
- **Standard**: Balanced analysis
- **Conservative**: Focus on risk/downside
- **Aggressive**: Focus on opportunities/upside
- **Educational**: Detailed explanations

### Historical Analysis

1. Navigate to "📜 Historical"
2. Select date range
3. Filter by ticker
4. Browse past snapshots
5. Load snapshot to view details

### Prediction Tracking

**Create Prediction:**
1. Run analysis first
2. Go to "🎯 Predictions"
3. Set target date and condition
4. System calculates probability
5. Save prediction

**Evaluate Prediction:**
1. Go to "Pending" tab
2. Enter actual price
3. Click "Evaluate"
4. View Brier score

**Track Accuracy:**
1. Go to "Evaluated" tab
2. View accuracy rate
3. Check Brier scores
4. Analyze prediction quality

### Tips & Best Practices

**Data Quality:**
- Use liquid underlyings (SPY, QQQ)
- Avoid close-to-expiry (<7 days)
- Check for data issues in error messages

**Interpretation:**
- Negative skew = bearish tilt
- High kurtosis = fat tails / crash risk
- Compare with historical patterns

**Predictions:**
- Track over time for calibration
- Low Brier score = good forecast
- Use for strategy validation

### Troubleshooting

**"Failed to fetch option data"**
- Check ticker symbol
- Try different expiration
- Market may be closed

**"SABR calibration failed"**
- System auto-falls back to spline
- Usually works fine with fallback
- Indicates unusual IV surface

**"Ollama not available"**
- System uses rule-based fallback
- Still provides interpretation
- Install Ollama for AI mode

**"Pattern matching unavailable"**
- Database may be empty
- Run more analyses first
- ChromaDB may not be installed

### API Keys Required

**FRED API Key** (Required)
- For risk-free rate
- Free from: https://fred.stlouisfed.org/docs/api/api_key.html
- Add to `.env` file

**Ollama** (Optional)
- For AI interpretation
- Install from: https://ollama.ai/download
- Pull model: `ollama pull qwen3:7b`
    """)

# Footer
st.markdown("---")
st.markdown("""
### Project Information

**Version**: 1.0.0
**Last Updated**: 2025-12-01
**Built With**: Claude Code

**GitHub**: [Coming Soon]
**Documentation**: See tabs above

**License**: MIT

**Acknowledgments**:
- Algorithm: Breeden & Litzenberger (1978)
- Data: OpenBB, Yahoo Finance, FRED
- AI: Ollama + Qwen3-7B
- Framework: Streamlit + Plotly
""")

st.caption("About | Option-Implied PDF Visualizer")
