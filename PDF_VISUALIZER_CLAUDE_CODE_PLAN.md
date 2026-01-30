# Option-Implied PDF Visualizer - Claude Code Development Plan
## Autonomous Build Guide | Version 1.0 | November 2025

---

# SECTION 1: PROJECT OVERVIEW

## 1.1 What We're Building
An interactive tool that extracts and visualizes option-implied probability density functions for SPX, showing where the market expects price to move, with AI-powered interpretation.

## 1.2 Core Features
1. **3D Probability Surface** - Strike × Time-to-Expiry × Probability
2. **AI Interpretation** - Plain English explanation of what the PDF shape means
3. **Historical Comparison** - "This shape looks like Oct 2023"
4. **Prediction Tracking** - Did the PDF predictions come true?
5. **Clean UI** - Professional Streamlit interface

## 1.3 Tech Stack
```
Backend:      Python 3.11+, FastAPI
Data:         OpenBB Terminal, yfinance (backup), FRED API
Math:         NumPy, SciPy, pySABR, Statsmodels
Visualization: Plotly
AI:           Qwen3-7B via Ollama (local) or GLM-4 via Z.ai API
Frontend:     Streamlit
Database:     SQLite + ChromaDB (for pattern matching)
Hosting:      HuggingFace Spaces (free)
```

## 1.4 Success Criteria
- [ ] Calculate accurate PDFs using Breeden-Litzenberger
- [ ] Display interactive 3D surface
- [ ] AI generates meaningful interpretation
- [ ] Loads in <5 seconds
- [ ] Deployable to HuggingFace Spaces

---

# SECTION 2: REQUIRED ACCOUNTS & APIs

## 2.1 Accounts Checklist

| Service | Purpose | Status | Action |
|---------|---------|--------|--------|
| OpenBB | SPY option chains | ⬜ Need | pip install openbb (no account needed) |
| FRED | Risk-free rate | ⬜ Need | Register at fred.stlouisfed.org/docs/api |
| HuggingFace | Hosting | ⬜ Need | Create account at huggingface.co |
| Ollama | Local LLM | ⬜ Need | Install from ollama.ai |

## 2.2 API Keys to Obtain

```bash
# Add these to .env file
FRED_API_KEY=your_fred_key  # Get from https://fred.stlouisfed.org/docs/api/api_key.html
HF_TOKEN=your_huggingface_token  # Optional, for private spaces
```

## 2.3 Local Setup Requirements

```bash
# Install Ollama (macOS)
brew install ollama

# Or Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Qwen3 model
ollama pull qwen3:7b

# Verify
ollama list
```

---

# SECTION 3: PROJECT STRUCTURE

```
pdf-visualizer/
├── .claude/
│   ├── CLAUDE.md              # Claude Code memory & instructions
│   ├── system_index.json      # Codebase index for Claude
│   └── dev_status.json        # Development progress tracking
│
├── docs/
│   ├── NAVIGATION.md          # Non-technical navigation guide
│   ├── RESUME_CONTEXT.md      # Session recovery document
│   ├── PROJECT_EXPLANATION.md # Technical & non-technical explanation
│   ├── PORTFOLIO.md           # Career documentation
│   └── API_REFERENCE.md       # API documentation
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── openbb_client.py   # OpenBB API wrapper (primary)
│   │   ├── yfinance_client.py # yfinance wrapper (backup)
│   │   ├── fred_client.py     # FRED API wrapper
│   │   └── cache.py           # Data caching layer
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── sabr.py            # SABR interpolation
│   │   ├── breeden_litz.py    # Breeden-Litzenberger PDF calculation
│   │   ├── statistics.py      # PDF statistics (skew, kurtosis, etc.)
│   │   └── patterns.py        # Historical pattern matching
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── interpreter.py     # AI interpretation agent
│   │   └── prompts.py         # Prompt templates
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── surface_3d.py      # 3D probability surface
│   │   ├── pdf_comparison.py  # 2D PDF overlay charts
│   │   └── probability_table.py # Probability tables
│   │
│   └── database/
│       ├── __init__.py
│       ├── models.py          # SQLite models
│       ├── history.py         # Historical PDF storage
│       └── predictions.py     # Prediction tracking
│
├── app/
│   ├── streamlit_app.py       # Main Streamlit application
│   ├── pages/
│   │   ├── 1_live_analysis.py
│   │   ├── 2_historical.py
│   │   ├── 3_predictions.py
│   │   └── 4_about.py
│   └── components/
│       ├── sidebar.py
│       ├── ai_panel.py
│       └── charts.py
│
├── tests/
│   ├── test_breeden_litz.py
│   ├── test_sabr.py
│   └── test_integration.py
│
├── config/
│   ├── settings.py            # App configuration
│   └── constants.py           # Constants (strikes, expirations, etc.)
│
├── .env.example
├── requirements.txt
├── README.md
├── Dockerfile
└── docker-compose.yml
```

---

# SECTION 4: PHASED DEVELOPMENT PLAN

## Phase 1: Foundation (Days 1-2)
**Goal**: Project setup, data pipeline working

### Tasks:
```
1.1 [ ] Initialize project structure
1.2 [ ] Create virtual environment & requirements.txt
1.3 [ ] Set up .env with API credentials
1.4 [ ] Build OpenBB client wrapper (primary data source)
1.5 [ ] Build yfinance client wrapper (backup)
1.6 [ ] Build FRED client for risk-free rate
1.7 [ ] Test data retrieval for SPY options
1.8 [ ] Create data caching layer
1.9 [ ] Write tests for data layer
```

### Validation:
```python
# Test: Can we fetch SPY option chain?
from src.data.openbb_client import get_spy_options
chain = get_spy_options()
assert len(chain) > 50, "Should have 50+ strikes"
print("✅ Phase 1 Complete")
```

---

## Phase 2: Core Math (Days 3-4)
**Goal**: Breeden-Litzenberger PDF calculation working

### Tasks:
```
2.1 [ ] Implement SABR calibration (or cubic spline fallback)
2.2 [ ] Build IV smile interpolation to fine grid
2.3 [ ] Implement Breeden-Litzenberger formula
2.4 [ ] Add PDF normalization (integrate to 1)
2.5 [ ] Calculate PDF statistics (mean, std, skew, kurtosis)
2.6 [ ] Calculate cumulative probabilities P(S<K)
2.7 [ ] Handle edge cases (negative densities, sparse data)
2.8 [ ] Write comprehensive tests
```

### Key Formula:
```python
# Breeden-Litzenberger
# f(K) = e^(rT) × ∂²C/∂K²

def breeden_litzenberger_pdf(strikes, call_prices, r, T):
    """
    Calculate risk-neutral PDF from call prices.
    
    Args:
        strikes: Array of strike prices
        call_prices: Corresponding call prices
        r: Risk-free rate
        T: Time to expiration (years)
    
    Returns:
        pdf: Probability density at each strike
    """
    dK = np.gradient(strikes)
    d2C_dK2 = np.gradient(np.gradient(call_prices, dK), dK)
    pdf = np.exp(r * T) * d2C_dK2
    pdf = np.maximum(pdf, 0)  # Ensure non-negative
    pdf = pdf / np.trapz(pdf, strikes)  # Normalize
    return pdf
```

### Validation:
```python
# Test: PDF should integrate to 1
from src.core.breeden_litz import calculate_pdf
pdf, strikes = calculate_pdf(chain, r=0.05, T=30/365)
integral = np.trapz(pdf, strikes)
assert 0.99 < integral < 1.01, f"PDF integrates to {integral}, should be ~1"
print("✅ Phase 2 Complete")
```

---

## Phase 3: Visualization (Days 5-6)
**Goal**: Interactive charts working

### Tasks:
```
3.1 [ ] Create 2D PDF plot (single expiration)
3.2 [ ] Create PDF comparison plot (multiple expirations overlay)
3.3 [ ] Build 3D surface (Strike × Time × Probability)
3.4 [ ] Add interactivity (hover, zoom, rotate)
3.5 [ ] Create probability table component
3.6 [ ] Apply dark theme styling
3.7 [ ] Optimize rendering performance
3.8 [ ] Test on different screen sizes
```

### 3D Surface Code:
```python
import plotly.graph_objects as go

def create_3d_surface(pdf_data: dict) -> go.Figure:
    """
    Create 3D probability surface.
    
    Args:
        pdf_data: Dict with expirations as keys, 
                  each containing 'strikes' and 'pdf' arrays
    """
    fig = go.Figure()
    
    # Prepare mesh data
    all_strikes = []
    all_days = []
    all_pdfs = []
    
    for exp, data in sorted(pdf_data.items(), key=lambda x: x[1]['days']):
        all_strikes.append(data['strikes'])
        all_days.append(np.full_like(data['strikes'], data['days']))
        all_pdfs.append(data['pdf'])
    
    fig.add_trace(go.Surface(
        x=np.array(all_strikes),
        y=np.array(all_days),
        z=np.array(all_pdfs),
        colorscale='Viridis',
        opacity=0.9,
        name='Probability Density'
    ))
    
    fig.update_layout(
        title='SPX Option-Implied Probability Surface',
        scene=dict(
            xaxis_title='Strike ($)',
            yaxis_title='Days to Expiry',
            zaxis_title='Probability Density',
            bgcolor='rgb(20,20,20)'
        ),
        paper_bgcolor='rgb(20,20,20)',
        font=dict(color='white'),
        width=900,
        height=700
    )
    
    return fig
```

### Validation:
```python
# Test: Chart renders without error
from src.visualization.surface_3d import create_3d_surface
fig = create_3d_surface(pdf_data)
fig.write_html("test_surface.html")
print("✅ Phase 3 Complete - Open test_surface.html to verify")
```

---

## Phase 4: AI Interpretation (Days 7-8)
**Goal**: AI generates meaningful analysis

### Tasks:
```
4.1 [ ] Set up Ollama connection (or Z.ai API fallback)
4.2 [ ] Create prompt templates for PDF analysis
4.3 [ ] Build interpretation pipeline
4.4 [ ] Add historical pattern matching
4.5 [ ] Generate comparison to past PDFs
4.6 [ ] Create prediction tracking system
4.7 [ ] Store interpretations in database
4.8 [ ] Test interpretation quality
```

### Prompt Template:
```python
PDF_ANALYSIS_PROMPT = """
You are a derivatives analyst interpreting option-implied probability densities.

Current SPX Price: {spot}
Analysis Date: {date}

30-Day PDF Statistics:
- Expected Price (Mean): ${mean:.2f}
- Standard Deviation: ${std:.2f}
- Implied Move: ±{implied_move:.1f}%
- Skewness: {skew:.3f} (negative = left tail heavy)
- Excess Kurtosis: {kurtosis:.3f} (>0 = fat tails)
- P(Down >5%): {p_down_5pct:.1f}%
- P(Up >5%): {p_up_5pct:.1f}%

Historical Context:
{historical_matches}

Provide analysis covering:
1. What the PDF shape indicates about market sentiment (2-3 sentences)
2. Tail risk assessment compared to normal distribution (1-2 sentences)
3. Historical comparison - what happened after similar PDF shapes (2-3 sentences)
4. Key takeaway for traders (1 sentence)

Be specific and quantitative. No fluff.
"""
```

### Validation:
```python
# Test: AI generates coherent response
from src.ai.interpreter import interpret_pdf
analysis = interpret_pdf(pdf_stats)
assert len(analysis) > 200, "Analysis should be substantive"
assert "skew" in analysis.lower() or "tail" in analysis.lower()
print("✅ Phase 4 Complete")
print(analysis)
```

---

## Phase 5: Database & History (Days 9-10)
**Goal**: Store and retrieve historical PDFs

### Tasks:
```
5.1 [ ] Design SQLite schema for PDF storage
5.2 [ ] Create models with SQLAlchemy
5.3 [ ] Build PDF archival system (daily snapshots)
5.4 [ ] Implement pattern matching (cosine similarity)
5.5 [ ] Set up ChromaDB for vector search (optional)
5.6 [ ] Create prediction tracking table
5.7 [ ] Build accuracy scoring system
5.8 [ ] Write database tests
```

### Schema:
```sql
-- PDF Snapshots
CREATE TABLE pdf_snapshots (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    spot_price REAL,
    expiration_days INTEGER,
    strikes BLOB,  -- JSON array
    pdf_values BLOB,  -- JSON array
    mean REAL,
    std REAL,
    skew REAL,
    kurtosis REAL,
    p_down_5pct REAL,
    p_up_5pct REAL
);

-- Predictions
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    created_at DATETIME,
    target_date DATE,
    predicted_probability REAL,
    strike_level REAL,
    condition TEXT,  -- 'above' or 'below'
    actual_outcome BOOLEAN,
    evaluated_at DATETIME
);

-- AI Interpretations
CREATE TABLE interpretations (
    id INTEGER PRIMARY KEY,
    pdf_snapshot_id INTEGER REFERENCES pdf_snapshots(id),
    interpretation TEXT,
    created_at DATETIME
);
```

---

## Phase 6: Streamlit App (Days 11-13)
**Goal**: Complete user interface

### Tasks:
```
6.1 [ ] Create main app structure
6.2 [ ] Build sidebar with controls
6.3 [ ] Implement Live Analysis page
6.4 [ ] Implement Historical page
6.5 [ ] Implement Predictions page
6.6 [ ] Implement About page
6.7 [ ] Add loading states and error handling
6.8 [ ] Apply consistent styling
6.9 [ ] Test all user flows
6.10 [ ] Optimize performance
```

### Main App Structure:
```python
# app/streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="SPX Probability Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📊 PDF Visualizer")
    ticker = st.selectbox("Ticker", ["SPX", "SPY"])
    refresh = st.button("🔄 Refresh Data")

# Main content
tab1, tab2, tab3 = st.tabs(["Live Analysis", "Historical", "Predictions"])

with tab1:
    # 3D Surface
    # AI Interpretation
    # Probability Table
    pass
```

---

## Phase 7: Testing & Deployment (Days 14-15)
**Goal**: Production-ready deployment

### Tasks:
```
7.1 [ ] Run all unit tests
7.2 [ ] Run integration tests
7.3 [ ] Performance testing (<5s load time)
7.4 [ ] Create Dockerfile
7.5 [ ] Test Docker build locally
7.6 [ ] Create HuggingFace Space
7.7 [ ] Configure secrets in HF
7.8 [ ] Deploy and test live
7.9 [ ] Create demo video
7.10 [ ] Write README
```

### Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### HuggingFace Space Config:
```yaml
# README.md header for HF Space
---
title: SPX Probability Visualizer
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app/streamlit_app.py
pinned: false
---
```

---

# SECTION 5: CLAUDE CODE INSTRUCTIONS

## 5.1 CLAUDE.md (Claude Memory File)

```markdown
# Claude Code Memory - PDF Visualizer Project

## Project Context
Building an option-implied probability density visualizer for SPY.
Uses Breeden-Litzenberger formula to extract risk-neutral PDF from options.

## Current Phase
[UPDATE THIS AS YOU PROGRESS]
Phase: 1 - Foundation
Status: In Progress
Last Updated: YYYY-MM-DD

## Key Decisions Made
- Using Streamlit (not React) for faster development
- Using Ollama locally (not paid API) for AI interpretation
- SQLite for storage (simple, no server needed)
- pySABR for IV interpolation (fallback to cubic spline)
- OpenBB + yfinance for data (100% free)

## Important Files
- src/core/breeden_litz.py - Core PDF calculation
- src/ai/interpreter.py - AI analysis
- app/streamlit_app.py - Main UI
- src/data/openbb_client.py - Primary data source

## API Credentials Location
- .env file (never commit)
- FRED_API_KEY

## Known Issues
[LOG ISSUES HERE]

## Commands
- Run app: `streamlit run app/streamlit_app.py`
- Run tests: `pytest tests/`
- Build docker: `docker build -t pdf-viz .`

## Next Steps
[UPDATE AFTER EACH SESSION]
```

## 5.2 System Index (JSON)

```json
{
  "project": "pdf-visualizer",
  "version": "1.0.0",
  "last_updated": "2025-11-27",
  "structure": {
    "entry_point": "app/streamlit_app.py",
    "core_modules": [
      "src/core/breeden_litz.py",
      "src/core/sabr.py",
      "src/data/theta_client.py"
    ],
    "ai_modules": [
      "src/ai/interpreter.py",
      "src/ai/prompts.py"
    ],
    "visualization": [
      "src/visualization/surface_3d.py",
      "src/visualization/pdf_comparison.py"
    ]
  },
  "dependencies": {
    "python": "3.11+",
    "key_packages": ["numpy", "scipy", "plotly", "streamlit", "openbb", "yfinance", "ollama"]
  },
  "api_integrations": {
    "openbb": {
      "purpose": "SPY option chain data (primary)",
      "auth": "none required"
    },
    "yfinance": {
      "purpose": "SPY option chain data (backup)",
      "auth": "none required"
    },
    "fred": {
      "purpose": "Risk-free rate",
      "auth": "API key in .env"
    },
    "ollama": {
      "purpose": "Local LLM for interpretation",
      "model": "qwen3:7b"
    }
  }
}
```

## 5.3 Development Status (JSON)

```json
{
  "project": "pdf-visualizer",
  "overall_progress": 0,
  "current_phase": 1,
  "phases": {
    "1": {
      "name": "Foundation",
      "status": "not_started",
      "progress": 0,
      "tasks": {
        "1.1": {"desc": "Initialize project structure", "done": false},
        "1.2": {"desc": "Create requirements.txt", "done": false},
        "1.3": {"desc": "Set up .env", "done": false},
        "1.4": {"desc": "Build OpenBB client", "done": false},
        "1.5": {"desc": "Build yfinance client (backup)", "done": false},
        "1.5": {"desc": "Build FRED client", "done": false},
        "1.6": {"desc": "Test data retrieval", "done": false},
        "1.7": {"desc": "Create caching layer", "done": false},
        "1.8": {"desc": "Write data layer tests", "done": false}
      }
    },
    "2": {
      "name": "Core Math",
      "status": "not_started",
      "progress": 0,
      "tasks": {
        "2.1": {"desc": "Implement SABR", "done": false},
        "2.2": {"desc": "IV interpolation", "done": false},
        "2.3": {"desc": "Breeden-Litzenberger", "done": false},
        "2.4": {"desc": "PDF normalization", "done": false},
        "2.5": {"desc": "PDF statistics", "done": false},
        "2.6": {"desc": "Cumulative probabilities", "done": false},
        "2.7": {"desc": "Edge case handling", "done": false},
        "2.8": {"desc": "Math tests", "done": false}
      }
    },
    "3": {
      "name": "Visualization",
      "status": "not_started",
      "progress": 0,
      "tasks": {}
    },
    "4": {
      "name": "AI Interpretation",
      "status": "not_started",
      "progress": 0,
      "tasks": {}
    },
    "5": {
      "name": "Database",
      "status": "not_started",
      "progress": 0,
      "tasks": {}
    },
    "6": {
      "name": "Streamlit App",
      "status": "not_started",
      "progress": 0,
      "tasks": {}
    },
    "7": {
      "name": "Deployment",
      "status": "not_started",
      "progress": 0,
      "tasks": {}
    }
  },
  "blockers": [],
  "notes": []
}
```

---

# SECTION 6: DOCUMENTATION TEMPLATES

## 6.1 NAVIGATION.md (Non-Technical Guide)

```markdown
# Navigation Guide - PDF Visualizer

## For Non-Technical Users

### What is this project?
A tool that shows where the stock market (specifically S&P 500) expects 
prices to go, based on how options are priced. Think of it as reading 
the market's "mind" about future price movements.

### How to use the app:
1. Open the website
2. The main chart shows probability of different price levels
3. Higher peaks = more likely prices
4. The AI panel explains what it all means in plain English

### Understanding the output:
- **3D Surface**: Mountains show likely prices, valleys show unlikely
- **Probability Table**: "There's a 30% chance SPX goes above 6000"
- **AI Analysis**: Plain English explanation of market sentiment

### Folder Guide (if you need to find something):
- `app/` - The actual website you see
- `docs/` - All documentation (you are here)
- `src/` - The code that does calculations (technical)
```

## 6.2 RESUME_CONTEXT.md (Session Recovery)

```markdown
# Resume Context - PDF Visualizer

## Quick Context for New Claude Code Session

### Project Summary
Option-implied PDF visualizer for SPY using Breeden-Litzenberger formula.
Streamlit app with 3D Plotly charts and AI interpretation via Ollama.
Data from OpenBB (free) with yfinance backup.

### Current State
[UPDATE AFTER EACH SESSION]
- **Phase**: X of 7
- **Last completed task**: X.X
- **Next task**: X.X
- **Any blockers**: None / [describe]

### Files Recently Modified
- [list files]

### Commands to Run
```bash
cd pdf-visualizer
source venv/bin/activate  # or: conda activate pdf-viz
streamlit run app/streamlit_app.py
```

### Known Issues to Address
- [list any bugs or issues]

### What to Do Next
1. [specific next step]
2. [following step]

### Key Context Claude Needs
- Using OpenBB for SPY options data (free)
- FRED API key in .env for risk-free rate
- Using Ollama with qwen3:7b model
- Breeden-Litzenberger formula in src/core/breeden_litz.py
```

## 6.3 PROJECT_EXPLANATION.md

```markdown
# Project Explanation - PDF Visualizer

## For Technical Users

### Architecture
```
Data Layer (OpenBB, yfinance, FRED)
    ↓
Processing Layer (SABR, Breeden-Litzenberger)
    ↓
AI Layer (Ollama/Qwen3)
    ↓
Presentation Layer (Streamlit + Plotly)
```

### Core Algorithm
The Breeden-Litzenberger formula extracts risk-neutral probability 
densities from option prices:

f(K) = e^(rT) × ∂²C/∂K²

Where:
- f(K) = probability density at strike K
- C = call option price
- r = risk-free rate
- T = time to expiration

### Key Technical Decisions
1. **SABR over cubic spline**: Better extrapolation in tails
2. **Ollama over OpenAI**: Free, local, no API costs
3. **SQLite over Postgres**: Simpler, no server needed
4. **Streamlit over React**: Faster development for MVP

---

## For Non-Technical Users

### What problem does this solve?
When you buy stock, you wonder "where will the price go?" 
This tool shows you what the market collectively thinks will happen,
based on how much people are paying for options (financial contracts).

### Why is this useful?
- See if the market expects a crash (fat left tail)
- See if options traders are bullish or bearish
- Get AI explanation in plain English
- Track if these predictions were accurate over time

### How accurate is it?
The tool shows what the market EXPECTS, not what WILL happen.
We track prediction accuracy to show how reliable these expectations are.
```

## 6.4 PORTFOLIO.md (Career Documentation)

```markdown
# Portfolio Documentation - PDF Visualizer

## Project Overview
**Name**: Option-Implied Probability Density Visualizer
**Duration**: 2-3 weeks
**Role**: Solo Developer (AI-assisted with Claude Code)
**Live Demo**: [HuggingFace Space URL]

---

## Problem Statement
Options traders and analysts need to understand market expectations 
for price movements. Existing tools either:
- Show raw option data without interpretation
- Require expensive Bloomberg/Refinitiv terminals
- Don't track prediction accuracy

---

## Solution
Built a free, open-source tool that:
1. Extracts probability distributions from option prices
2. Visualizes in interactive 3D
3. Provides AI-powered interpretation
4. Tracks prediction accuracy over time

---

## Technical Implementation

### Architecture Decisions
| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Visualization | Matplotlib, Plotly, D3 | Plotly | Interactive 3D, Python native |
| AI | OpenAI, Anthropic, Local | Ollama | Free, no API costs, privacy |
| Frontend | React, Streamlit, Gradio | Streamlit | Fastest for data apps |
| Database | Postgres, SQLite, MongoDB | SQLite | Simple, serverless |

### Key Algorithms
- **Breeden-Litzenberger**: Extracts risk-neutral PDF from option prices
- **SABR Model**: Interpolates implied volatility smile
- **Cosine Similarity**: Matches current PDF to historical patterns

### Tech Stack
```
Python 3.11 | NumPy | SciPy | Plotly | Streamlit
OpenBB | yfinance | FRED API | Ollama (Qwen3-7B)
SQLite | Docker | HuggingFace Spaces
```

---

## Skills Demonstrated

### Quantitative Finance
- Options pricing theory
- Risk-neutral valuation
- Implied volatility modeling (SABR)
- Probability distributions

### Software Engineering
- Clean architecture (separation of concerns)
- API integration
- Data pipeline design
- Containerization (Docker)

### AI/ML
- LLM integration for interpretation
- Prompt engineering
- Vector similarity for pattern matching

### Product Thinking
- User-centric design
- MVP scoping
- Free-tier optimization

---

## Challenges & Solutions

### Challenge 1: Noisy Option Data
**Problem**: Raw option quotes have bad ticks and wide spreads
**Solution**: SABR interpolation + outlier filtering

### Challenge 2: PDF Tails
**Problem**: Extreme strikes have unreliable prices
**Solution**: Constrain to ±20% from spot, smooth extrapolation

### Challenge 3: AI Hallucination
**Problem**: LLM might make up statistics
**Solution**: Pass only calculated stats to LLM, constrain to interpretation only

---

## Results & Impact
- Deployed to HuggingFace Spaces (free hosting)
- [X] users in first month
- PDF predictions tracked at [Y]% accuracy
- Featured in [any mentions]

---

## Future Enhancements
- Add more tickers (SPY, QQQ, individual stocks)
- Real-time streaming updates
- Alerting when PDF shape changes dramatically
- Monetization via premium features

---

## Code Repository
- GitHub: [URL]
- HuggingFace: [URL]
- Documentation: [URL]

---

## Interview Talking Points

### "Walk me through this project"
"I built a tool that extracts probability distributions from option prices 
using the Breeden-Litzenberger formula. The key insight is that options 
prices embed market expectations - by taking the second derivative of call 
prices with respect to strike, you get the risk-neutral PDF. I added AI 
interpretation to make it accessible and track prediction accuracy to 
validate the signal."

### "What was the hardest part?"
"Handling noisy option data in the tails. Extreme strikes have wide 
bid-ask spreads and few trades, so I used SABR interpolation to generate 
a smooth volatility surface before applying Breeden-Litzenberger."

### "Why didn't you use [X]?"
"I considered [X] but chose [Y] because [specific reason related to 
constraints: cost, complexity, time, or fit for purpose]."
```

---

# SECTION 7: QUICK START FOR CLAUDE CODE

## Initial Prompt to Begin

```
I'm building an Option-Implied PDF Visualizer for SPY. 

Read the development plan at /path/to/PDF_VISUALIZER_CLAUDE_CODE_PLAN.md

Start with Phase 1: Foundation
- Initialize the project structure as specified
- Create requirements.txt with necessary packages
- Set up the .env.example file
- Build the OpenBB client wrapper for SPY options
- Build yfinance client as backup

I have FRED API key ready. Data sources are 100% free (OpenBB + yfinance).
```

## Between-Session Resume Prompt

```
Continuing work on PDF Visualizer project.

Read:
1. docs/RESUME_CONTEXT.md for current state
2. .claude/dev_status.json for task progress
3. .claude/CLAUDE.md for project memory

Continue from where we left off.
```

---

# SECTION 8: REQUIREMENTS.TXT

```
# Core
numpy>=1.24.0
scipy>=1.11.0
pandas>=2.0.0

# Data Sources (FREE)
openbb>=4.0.0
yfinance>=0.2.0
fredapi>=0.5.0
requests>=2.31.0

# Visualization
plotly>=5.18.0
streamlit>=1.28.0

# AI
ollama>=0.1.0

# Database
sqlalchemy>=2.0.0
chromadb>=0.4.0

# Math/Finance
pysabr>=0.2.0
statsmodels>=0.14.0
empyrical>=0.5.5

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Dev
black>=23.0.0
isort>=5.12.0
```

---

# SECTION 9: CHECKLIST SUMMARY

## Pre-Development
- [ ] Install OpenBB: `pip install openbb`
- [ ] Get FRED API key
- [ ] Create HuggingFace account
- [ ] Install Ollama locally
- [ ] Pull qwen3:7b model

## Phase Completion
- [ ] Phase 1: Foundation
- [ ] Phase 2: Core Math
- [ ] Phase 3: Visualization
- [ ] Phase 4: AI Interpretation
- [ ] Phase 5: Database
- [ ] Phase 6: Streamlit App
- [ ] Phase 7: Deployment

## Post-Deployment
- [ ] README complete
- [ ] Demo video recorded
- [ ] Portfolio documentation done
- [ ] Shared on LinkedIn/Twitter
- [ ] Added to personal website

---

*Document Version: 1.0*
*Created: November 2025*
*For: Claude Code Autonomous Development*
