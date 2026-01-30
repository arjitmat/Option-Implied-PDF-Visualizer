# Project Navigation Guide

**For Non-Technical Users**: This guide helps you understand the project structure without needing to know how to code.

## Quick Start

### What This Project Does
This tool analyzes stock options to predict where the market thinks SPY/SPX prices will move. It creates beautiful 3D visualizations and provides AI-powered explanations in plain English.

### Key Features
1. **3D Probability Surface** - See market expectations in 3D
2. **AI Interpretation** - Get plain English explanations
3. **Historical Comparison** - Compare with past market conditions
4. **Prediction Tracking** - See if the predictions were accurate

---

## Project Structure (Simplified)

### 📁 Main Folders

#### `/app/` - The Application
- This is where the Streamlit web interface will live
- **Status**: Not yet built (coming in Phase 6)
- **What it does**: Provides the user interface you'll interact with

#### `/src/` - The Engine
This is where all the "magic" happens. Contains all the core logic.

**Subfolders**:
- `/data/` - Gets option prices from the internet
- `/core/` - Does the math calculations
- `/ai/` - Provides AI-powered interpretations
- `/visualization/` - Creates the charts and 3D graphics
- `/database/` - Stores historical data (coming in Phase 5)

#### `/tests/` - Quality Assurance
- Automated tests to ensure everything works correctly
- **Status**: Comprehensive tests for Phases 1-4

#### `/docs/` - Documentation
- This file and other guides
- Technical explanations
- Career documentation

#### `/config/` - Settings
- Configuration files
- Constants and parameters

#### `/.claude/` - Development Tracking
- Claude Code's memory and tracking files
- Phase progress tracking
- System index

---

## How to Find Things

### Want to understand the core algorithm?
→ Look at `src/core/breeden_litz.py`
→ Read the README.md "Core Algorithm" section

### Want to see the visualizations?
→ Check `src/visualization/` folder
→ The 3D surface is in `surface_3d.py`
→ The 2D plots are in `pdf_2d.py`

### Want to understand the AI interpretation?
→ Look at `src/ai/interpreter.py`
→ See prompt templates in `src/ai/prompts.py`

### Want to know where data comes from?
→ Check `src/data/data_manager.py` (main interface)
→ See individual clients: `openbb_client.py`, `yfinance_client.py`, `fred_client.py`

### Want to check project status?
→ Read `.claude/dev_status.json` for detailed progress
→ Read `README.md` for overview
→ Check `.claude/CLAUDE.md` for Claude's memory

---

## Development Phases Explained

### ✅ Phase 1: Foundation (COMPLETE)
**What it did**: Set up the infrastructure to get data from the internet
**Key files**: Everything in `/src/data/`

### ✅ Phase 2: Core Math (COMPLETE)
**What it did**: Implemented the Breeden-Litzenberger formula to extract probabilities
**Key files**: Everything in `/src/core/`
**Star of the show**: `breeden_litz.py`

### ✅ Phase 3: Visualization (COMPLETE)
**What it did**: Created beautiful 3D charts and interactive plots
**Key files**: Everything in `/src/visualization/`
**Flagship feature**: 3D probability surface

### ✅ Phase 4: AI Interpretation (COMPLETE)
**What it did**: Added AI to explain what the charts mean in plain English
**Key files**: Everything in `/src/ai/` and pattern matching in `/src/core/patterns.py`
**Note**: Ollama installation pending (optional)

### ✅ Phase 5: Database & History (COMPLETE)
**What it did**: Store historical data and track prediction accuracy
**Key files**: Everything in `/src/database/`

### ✅ Phase 6: Streamlit App (COMPLETE)
**What it did**: Created the web interface you can actually use
**Key files**: Everything in `/app/`

### ✅ Phase 7: Deployment (COMPLETE)
**What it did**: Docker configuration for deployment
**Key files**: Dockerfile, docker-compose.yml

### ✅ Phase 8: React Frontend (COMPLETE)
**What it did**: Built premium React SPA with FastAPI backend
**Key files**: `/frontend/` (React), `/backend/` (FastAPI)

---

## Configuration Files

### `.env` - Secrets and API Keys
- Contains your FRED API key
- **NEVER commit this to Git**
- **NEVER share publicly**

### `requirements.txt` - Python Dependencies
- Lists all the libraries needed to run the project
- Used by `pip install -r requirements.txt`

### `config/settings.py` - Application Settings
- Cache durations
- Database paths
- Default parameters

### `config/constants.py` - Application Constants
- SABR model parameters
- Strike ranges
- Visualization settings

---

## Testing

### How to run tests:
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core_math.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test files:
- `test_data_layer.py` - Tests data fetching
- `test_core_math.py` - Tests PDF calculations
- `test_visualization.py` - Tests chart generation
- `test_ai_components.py` - Tests AI interpretation

---

## Common Tasks

### How to get option data:
```python
from src.data.data_manager import DataManager
dm = DataManager()
options = dm.get_options(ticker="SPY")
```

### How to calculate a PDF:
```python
from src.core.breeden_litz import BreedenlitzenbergPDF
pdf_calc = BreedenlitzenbergPDF()
pdf = pdf_calc.calculate_pdf(
    strikes=strikes,
    implied_vols=ivs,
    spot=spot,
    r=risk_free_rate,
    T=time_to_expiry
)
```

### How to create a 3D surface:
```python
from src.visualization.surface_3d import create_3d_surface
fig = create_3d_surface(pdf_data, spot_price=450)
fig.show()
```

### How to get AI interpretation:
```python
from src.ai.interpreter import PDFInterpreter
interpreter = PDFInterpreter(mode='standard')
result = interpreter.interpret_single_pdf(
    ticker="SPY",
    spot=450,
    stats=stats,
    days_to_expiry=30
)
print(result['interpretation'])
```

---

## Data Flow (High Level)

1. **Fetch Data** → DataManager gets option chain from OpenBB/yfinance
2. **Get Risk-Free Rate** → FRED client fetches treasury rate
3. **Interpolate IV** → SABR model smooths implied volatility curve
4. **Calculate PDF** → Breeden-Litzenberger extracts probabilities
5. **Calculate Stats** → PDFStatistics computes mean, std, skew, etc.
6. **Find Patterns** → PDFPatternMatcher searches historical data
7. **Generate Interpretation** → PDFInterpreter creates analysis
8. **Visualize** → Plotly creates interactive charts

---

## Need Help?

### Documentation:
- Start with `README.md` for overview
- Check `.claude/CLAUDE.md` for development context
- Read this file for navigation
- See `PROJECT_EXPLANATION.md` for detailed explanation

### Resources:
- OpenBB docs: https://docs.openbb.co
- FRED API: https://fred.stlouisfed.org/docs/api/
- Ollama: https://ollama.ai
- Plotly: https://plotly.com/python/

### Claude Code:
- This project was built with Claude Code
- All development tracked in `.claude/` folder
- Session recovery via `RESUME_CONTEXT.md`

---

## License & Credits

**License**: MIT

**Built with**:
- Claude Code (AI pair programmer)
- OpenBB Terminal (data)
- Ollama + Qwen3-7B (AI interpretation)
- Plotly (visualizations)
- Streamlit (web UI)

---

**Last Updated**: 2025-12-08 | **Phase**: 8 Complete (100% - Production Ready)
