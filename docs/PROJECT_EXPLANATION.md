# Option-Implied PDF Visualizer - Complete Project Explanation

## Executive Summary

This project extracts market expectations about future stock prices from options markets and presents them as intuitive 3D visualizations with AI-powered interpretations.

**Status**: ✅ Phase 8 Complete (100% - Production Ready)
**Last Updated**: 2025-12-08
**Repository Type**: Solo project with AI assistance (Claude Code)
**Live Interfaces**: Streamlit (port 8501) + React SPA (port 5173 + FastAPI backend 8000)

---

## Table of Contents

1. [Non-Technical Explanation](#non-technical-explanation)
2. [Technical Explanation](#technical-explanation)
3. [Architecture Overview](#architecture-overview)
4. [Mathematical Foundation](#mathematical-foundation)
5. [Implementation Details](#implementation-details)
6. [Key Algorithms](#key-algorithms)
7. [Data Flow](#data-flow)
8. [Testing Strategy](#testing-strategy)
9. [Future Enhancements](#future-enhancements)

---

## Non-Technical Explanation

### What Problem Does This Solve?

When traders buy and sell options, they're essentially placing bets on where they think a stock price will go. These bets contain valuable information about the market's collective expectations. This tool extracts that hidden information and makes it visible.

### What Does It Do?

Imagine you could see a 3D landscape showing:
- **X-axis**: Different possible stock prices (strikes)
- **Y-axis**: Time into the future (days to expiration)
- **Z-axis**: How likely each price is (probability)

The tool creates this landscape and then uses AI to explain what it means in plain English.

### Why Is This Useful?

**For Traders**: Understand where the market expects prices to move and how much uncertainty exists.

**For Risk Managers**: Quantify tail risk and see probability distributions.

**For Researchers**: Study historical probability distributions and prediction accuracy.

**For Students**: Learn derivatives pricing and market microstructure.

### Real-World Example

Imagine SPY is trading at $450. The tool might show:
- 68% chance price stays between $436-$467 in 30 days
- 22% chance of +5% move (bullish tilt)
- 18% chance of -5% move
- Negative skewness (-0.15) suggests slight downside bias
- The AI explains: "Market is pricing in moderate uncertainty with slight bearish lean, similar to pre-Fed-announcement patterns in October 2023."

---

## Technical Explanation

### Core Concept: Risk-Neutral Probability Density

Options markets implicitly encode a **risk-neutral probability distribution** for future asset prices. The Breeden-Litzenberger (1978) formula allows us to extract this distribution by taking the second derivative of call option prices with respect to strike:

```
f(K) = e^(rT) × ∂²C/∂K²
```

Where:
- `f(K)` = risk-neutral probability density at strike K
- `C` = call option price as a function of strike
- `r` = risk-free rate
- `T` = time to expiration
- `e^(rT)` = discount factor

### Why This Matters

**Traditional Approach**: Implied volatility gives a single number (expected magnitude of moves)

**This Approach**: Full probability distribution showing:
- Mean and variance (expected price and uncertainty)
- Skewness (directional bias)
- Kurtosis (fat tails / crash risk)
- Specific probabilities for any price level

### Technical Stack

**Backend**:
- Python 3.11+ (type hints, modern syntax)
- NumPy/SciPy (numerical computation)
- Pandas (data manipulation)

**Data Sources**:
- OpenBB Terminal (primary option chain data)
- yfinance (backup data source)
- FRED API (risk-free rate)

**Models**:
- SABR (Stochastic Alpha Beta Rho) volatility model
- Cubic spline interpolation (fallback)
- Cosine similarity for pattern matching

**AI**:
- Ollama (local LLM inference)
- Qwen3-7B (7 billion parameter language model)
- Intelligent fallback for offline operation

**Visualization**:
- Plotly (interactive 3D graphics)
- Dark theme with professional styling

**Database** (Phase 5):
- SQLite (time series storage)
- ChromaDB (vector search for patterns)

**Frontend** (Phase 6):
- Streamlit (Python web framework)

**Deployment** (Phase 7):
- Docker containerization
- HuggingFace Spaces hosting

---

## Architecture Overview

### Layer 1: Data Acquisition

```
┌─────────────────────────────────────────┐
│         DataManager (Facade)            │
│  ┌─────────────────────────────────┐   │
│  │  OpenBB Client (Primary)        │   │
│  │  YFinance Client (Backup)       │   │
│  │  FRED Client (Risk-Free Rate)   │   │
│  └─────────────────────────────────┘   │
│            ↓                            │
│  ┌─────────────────────────────────┐   │
│  │  Cache Layer (15min TTL)        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Design Pattern**: Facade pattern with automatic fallback
**Resilience**: Dual data sources, file-based caching
**Performance**: Minimizes API calls via intelligent caching

### Layer 2: Mathematical Core

```
┌─────────────────────────────────────────┐
│     BreedenlitzenbergPDF                │
│  ┌─────────────────────────────────┐   │
│  │  1. SABR Calibration            │   │
│  │  2. IV Interpolation            │   │
│  │  3. Call Price Calculation      │   │
│  │  4. Numerical Differentiation   │   │
│  │  5. PDF Normalization           │   │
│  └─────────────────────────────────┘   │
│            ↓                            │
│  ┌─────────────────────────────────┐   │
│  │  PDFStatistics Calculator       │   │
│  │  (mean, std, skew, kurtosis)    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Design Pattern**: Pipeline pattern
**Numerical Methods**: Savitzky-Golay smoothing, gradient-based derivatives
**Robustness**: Edge case handling, non-negativity constraints

### Layer 3: AI Interpretation

```
┌─────────────────────────────────────────┐
│        PDFInterpreter                   │
│  ┌─────────────────────────────────┐   │
│  │  PDFPatternMatcher              │   │
│  │  (cosine similarity)            │   │
│  └─────────────────────────────────┘   │
│            ↓                            │
│  ┌─────────────────────────────────┐   │
│  │  Ollama Client                  │   │
│  │  (with fallback)                │   │
│  └─────────────────────────────────┘   │
│            ↓                            │
│  ┌─────────────────────────────────┐   │
│  │  Prompt Templates               │   │
│  │  (4 analysis modes)             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Design Pattern**: Strategy pattern (4 interpretation modes)
**AI Architecture**: Local LLM with graceful degradation
**Pattern Matching**: 70% shape similarity + 30% statistical similarity

### Layer 4: Visualization

```
┌─────────────────────────────────────────┐
│      Plotly Visualization Suite         │
│  ┌─────────────────────────────────┐   │
│  │  2D PDF Plots                   │   │
│  │  PDF Comparison Plots           │   │
│  │  CDF Plots                      │   │
│  └─────────────────────────────────┘   │
│            +                            │
│  ┌─────────────────────────────────┐   │
│  │  3D Surface (Strike×Time×Prob)  │   │
│  │  Heatmap (2D alternative)       │   │
│  │  Wireframe (skeleton view)      │   │
│  └─────────────────────────────────┘   │
│            +                            │
│  ┌─────────────────────────────────┐   │
│  │  Probability Tables             │   │
│  │  (color-coded, interactive)     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Design Pattern**: Factory pattern for plot creation
**Theming**: Dark theme with consistent styling
**Interactivity**: Full Plotly features (hover, zoom, rotate)

---

## Mathematical Foundation

### 1. Breeden-Litzenberger Formula (Core Algorithm)

**Derivation**:

The price of a European call option can be expressed as:
```
C(K) = e^(-rT) × ∫[K to ∞] (S - K) × f(S) dS
```

Taking the first derivative:
```
∂C/∂K = -e^(-rT) × ∫[K to ∞] f(S) dS = -e^(-rT) × P(S > K)
```

Taking the second derivative:
```
∂²C/∂K² = e^(-rT) × f(K)
```

Rearranging:
```
f(K) = e^(rT) × ∂²C/∂K²
```

**Implementation Challenges**:
1. Need smooth call price function → Use SABR interpolation
2. Numerical differentiation is noisy → Apply Savitzky-Golay filter
3. Can produce negative densities → Enforce non-negativity
4. Must integrate to 1 → Normalize using trapezoid rule

### 2. SABR Volatility Model

**Model Equations**:
```
dF = α × F^β × dW₁
dα = ν × α × dW₂
dW₁ × dW₂ = ρ dt
```

**Parameters**:
- `α` = volatility of volatility
- `β` = elasticity (typically 0.5 for equities)
- `ρ` = correlation between price and volatility
- `ν` = vol-of-vol

**Calibration**: Minimize sum of squared errors between market IV and model IV using Nelder-Mead optimization.

**Why SABR?**: Captures volatility smile/skew better than Black-Scholes, industry standard for equity options.

### 3. Pattern Matching Algorithm

**Similarity Score**:
```
similarity = 0.7 × shape_similarity + 0.3 × stats_similarity
```

**Shape Similarity** (Cosine):
```
cos(θ) = (A · B) / (||A|| × ||B||)
```
Where A and B are PDF vectors.

**Stats Similarity**:
```
sim = 1 - mean_abs_diff([skew, kurtosis, implied_move])
```

**Why This Works**: Combines global shape (cosine) with specific moments (stats) to find truly similar distributions.

---

## Implementation Details

### Phase 1: Foundation (100% Complete)

**Files Created**:
- `src/data/openbb_client.py` (169 lines)
- `src/data/yfinance_client.py` (142 lines)
- `src/data/fred_client.py` (89 lines)
- `src/data/cache.py` (98 lines)
- `src/data/data_manager.py` (186 lines)

**Key Features**:
- Automatic fallback between data sources
- File-based caching with TTL
- Comprehensive error handling
- Type hints throughout

**Testing**: 15 tests covering normal operation and edge cases

### Phase 2: Core Math (100% Complete)

**Files Created**:
- `src/core/breeden_litz.py` (287 lines) ⭐ **CORE ALGORITHM**
- `src/core/sabr.py` (201 lines)
- `src/core/statistics.py` (234 lines)

**Key Features**:
- SABR calibration with fallback to cubic spline
- Breeden-Litzenberger with numerical smoothing
- Complete PDF statistics (13 metrics)
- CDF and probability queries

**Testing**: 22 tests covering calculation accuracy and edge cases

### Phase 3: Visualization (100% Complete)

**Files Created**:
- `src/visualization/themes.py` (73 lines)
- `src/visualization/pdf_2d.py` (312 lines)
- `src/visualization/surface_3d.py` (264 lines)
- `src/visualization/probability_table.py` (189 lines)

**Key Features**:
- Dark theme configuration system
- 4 types of 2D plots
- 3 types of 3D visualizations
- 4 types of probability tables
- Full interactivity

**Testing**: 18 tests covering plot generation and formatting

### Phase 4: AI Interpretation (100% Complete)

**Files Created**:
- `src/ai/prompts.py` (198 lines)
- `src/ai/interpreter.py` (245 lines)
- `src/core/patterns.py` (276 lines)

**Key Features**:
- 4 interpretation modes (standard, conservative, aggressive, educational)
- Pattern matching with cosine similarity
- Ollama client with graceful fallback
- Rule-based interpretation system

**Testing**: 21 tests covering AI components and pattern matching

### Phases 5-7: Pending

**Phase 5**: SQLite schema, SQLAlchemy models, prediction tracking
**Phase 6**: Streamlit UI with 4 pages
**Phase 7**: Docker, testing, deployment to HuggingFace Spaces

---

## Key Algorithms

### Algorithm 1: PDF Extraction

```python
def _breeden_litzenberger(self, strikes, call_prices, r, T):
    """
    Extract risk-neutral PDF from call prices.

    f(K) = e^(rT) × ∂²C/∂K²
    """
    # Calculate gradients (numerical derivatives)
    dK = np.gradient(strikes)
    dC_dK = np.gradient(call_prices, strikes)
    d2C_dK2 = np.gradient(dC_dK, strikes)

    # Apply Breeden-Litzenberger formula
    pdf = np.exp(r * T) * d2C_dK2

    # Enforce non-negativity
    pdf = np.maximum(pdf, 0)

    # Normalize to integrate to 1
    pdf = pdf / np.trapz(pdf, strikes)

    return pdf
```

**Complexity**: O(n) where n = number of strikes
**Accuracy**: Depends on strike density and IV smoothness

### Algorithm 2: SABR Calibration

```python
def calibrate(self, strikes, implied_vols, forward, tau):
    """
    Calibrate SABR to market IV smile.
    """
    def objective(params):
        alpha, rho, nu = params
        model_vols = self._sabr_formula(strikes, forward, alpha, rho, nu, self.beta, tau)
        return np.sum((model_vols - implied_vols) ** 2)

    initial_guess = [0.2, -0.3, 0.4]
    bounds = [(0.001, 2.0), (-0.999, 0.999), (0.001, 2.0)]

    result = minimize(
        objective,
        initial_guess,
        method='Nelder-Mead',
        bounds=bounds,
        options={'maxiter': 1000}
    )

    self.alpha, self.rho, self.nu = result.x
    return result
```

**Complexity**: O(m × n) where m = iterations, n = strikes
**Convergence**: Typically <100 iterations for equity options

### Algorithm 3: Pattern Matching

```python
def _calculate_similarity(self, current_pdf, current_strikes, hist_pdf, hist_strikes, current_stats, hist_stats):
    """
    Calculate combined similarity score.
    """
    # Shape similarity (cosine)
    shape_sim = self._pdf_shape_similarity(
        current_pdf, current_strikes,
        hist_pdf, hist_strikes
    )

    # Statistical similarity
    stats_sim = self._stats_similarity(current_stats, hist_stats)

    # Weighted combination
    return 0.7 * shape_sim + 0.3 * stats_sim
```

**Complexity**: O(n) for interpolation + O(n) for dot product
**Accuracy**: Validated against synthetic test cases

---

## Data Flow

### Complete Pipeline (End-to-End)

```
1. User Request
   ↓
2. DataManager.get_options("SPY")
   ├─> OpenBB Client (try primary)
   └─> YFinance Client (fallback if needed)
   ↓
3. FREDClient.get_risk_free_rate()
   ↓
4. SABRModel.calibrate(strikes, IVs)
   ├─> Optimize α, ρ, ν parameters
   └─> Fallback to CubicSpline if fails
   ↓
5. SABRModel.interpolate_iv(fine_strikes)
   ↓
6. BreedenlitzenbergPDF.calculate_pdf(strikes, IVs, spot, r, T)
   ├─> Calculate call prices
   ├─> Apply Breeden-Litzenberger formula
   ├─> Smooth with Savitzky-Golay
   └─> Normalize to integrate to 1
   ↓
7. PDFStatistics.calculate_all_stats()
   ├─> Mean, std, skewness, kurtosis
   ├─> Implied move, tail probabilities
   └─> Confidence intervals
   ↓
8. PDFPatternMatcher.find_similar_patterns()
   ├─> Load historical PDFs
   ├─> Calculate similarity scores
   └─> Return top matches
   ↓
9. PDFInterpreter.interpret_single_pdf()
   ├─> Format prompt with stats & patterns
   ├─> Try Ollama.generate()
   └─> Fallback to rule-based if Ollama unavailable
   ↓
10. Visualization Functions
    ├─> create_3d_surface()
    ├─> plot_pdf_2d()
    ├─> create_probability_table()
    └─> Return interactive Plotly figures
    ↓
11. Return Results to User
    ├─> PDF values & strikes
    ├─> All statistics
    ├─> Pattern matches
    ├─> AI interpretation
    └─> Plotly figures
```

### Data Flow Timing (Approximate)

- Data fetch: ~1-3 seconds (or instant if cached)
- SABR calibration: ~0.1-0.5 seconds
- PDF calculation: ~0.05 seconds
- Statistics: ~0.01 seconds
- Pattern matching: ~0.1-1 second (depends on history size)
- AI interpretation: ~2-5 seconds (or ~0.01s for fallback)
- Visualization: ~0.1-0.5 seconds

**Total**: 3-10 seconds for complete analysis

---

## Testing Strategy

### Unit Tests

**Coverage**: High coverage across all modules

**Approach**:
- Test normal operation
- Test edge cases (empty data, extreme values)
- Test error conditions
- Test fallback mechanisms

**Example** (from `test_core_math.py`):
```python
def test_pdf_normalization():
    """Ensure PDF integrates to 1.0."""
    pdf_calc = BreedenlitzenbergPDF()
    pdf = pdf_calc.calculate_pdf(...)
    integral = trapz(pdf, strikes)
    assert abs(integral - 1.0) < 1e-6
```

### Integration Tests

**Example** (from `test_ai_components.py`):
```python
def test_integration_ai_workflow():
    """Test complete AI workflow end-to-end."""
    # 1. Create PDF
    # 2. Calculate statistics
    # 3. Find patterns
    # 4. Generate interpretation
    # All steps must complete successfully
```

### Fallback Tests

**Critical**: Ensure system works when external dependencies fail

**Tests**:
- OpenBB fails → YFinance succeeds
- SABR fails → Cubic spline succeeds
- Ollama unavailable → Rule-based interpretation succeeds

---

## Future Enhancements

### Phase 5: Database & History

**Schema Design**:
```sql
CREATE TABLE pdf_snapshots (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    ticker TEXT,
    days_to_expiry INTEGER,
    spot_price REAL,
    strikes BLOB,
    pdf_values BLOB,
    stats JSON,
    interpretation TEXT,
    model_used TEXT
);

CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    forecast_date DATETIME,
    target_date DATETIME,
    predicted_prob REAL,
    condition TEXT,
    target_level REAL,
    actual_outcome BOOLEAN,
    actual_price REAL,
    evaluation_date DATETIME
);

CREATE TABLE pattern_matches (
    id INTEGER PRIMARY KEY,
    current_snapshot_id INTEGER,
    historical_snapshot_id INTEGER,
    similarity_score REAL,
    shape_similarity REAL,
    stats_similarity REAL
);
```

**ChromaDB Integration**:
- Store PDF embeddings for vector search
- Fast similarity search across thousands of historical PDFs

### Phase 6: Streamlit App

**Pages**:
1. **Live Analysis**: Real-time PDF extraction and visualization
2. **Historical**: Browse past PDFs and patterns
3. **Predictions**: Track accuracy of market expectations
4. **About**: Documentation and explanation

**Features**:
- Ticker selection
- Expiration date selection
- Analysis mode selection
- Export to CSV/PNG
- Dark/light theme toggle

### Phase 7: Deployment

**Docker**:
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app/streamlit_app.py"]
```

**HuggingFace Spaces**:
- Free hosting for ML demos
- Automatic builds from Git
- Environment variables for API keys

---

## Technical Challenges & Solutions

### Challenge 1: Noisy Numerical Derivatives

**Problem**: ∂²C/∂K² amplifies noise in option prices
**Solution**:
1. Use SABR to interpolate IV (creates smooth curve)
2. Apply Savitzky-Golay filter (polynomial smoothing)
3. Use dense strike grid (200+ points)

### Challenge 2: Data Source Reliability

**Problem**: APIs can be down or rate-limited
**Solution**:
1. Dual data sources (OpenBB + yfinance)
2. Automatic fallback in DataManager
3. File-based caching (15min TTL)

### Challenge 3: SABR Calibration Failures

**Problem**: Sometimes fails to converge
**Solution**:
1. Fallback to cubic spline interpolation
2. Graceful degradation (still produces PDF)
3. Log warnings for debugging

### Challenge 4: Ollama Availability

**Problem**: User may not have Ollama installed
**Solution**:
1. Check availability at runtime
2. Provide rule-based interpretation fallback
3. Fallback quality is surprisingly good (tested)

---

## Performance Optimization

### Current Performance

**Bottlenecks**:
1. API calls (1-3 seconds) → Mitigated by caching
2. SABR calibration (~0.3 seconds) → Acceptable
3. Pattern matching (~0.5 seconds) → Will improve with indexing

**Future Optimizations**:
1. **Database indexing**: Speed up historical queries
2. **Caching layer**: Redis for distributed caching
3. **Parallel processing**: Multiple expirations in parallel
4. **Incremental updates**: Only recalculate changed data

---

## Conclusion

This project demonstrates:
- **Advanced quantitative finance**: Option-implied probabilities
- **Robust software engineering**: Error handling, fallbacks, testing
- **Modern ML/AI**: Local LLM integration with graceful degradation
- **Interactive visualization**: 3D graphics with full interactivity
- **Production-ready code**: Type hints, documentation, comprehensive tests

**Current Status**: 57% complete (4/7 phases)
**Next Milestone**: Phase 5 - Database & History
**Timeline**: Ready for deployment after Phase 7

---

**Last Updated**: 2025-12-01
**Author**: Built with Claude Code
**License**: MIT
