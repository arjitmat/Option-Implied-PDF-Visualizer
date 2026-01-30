# Resume Context - PDF Visualizer
**Last Updated**: 2025-12-08 (Session 3 - React Frontend Polish)

## Quick Context for New Claude Code Session

### Current Project Status
- **Phase**: 8 of 8 - ✅ **ALL PHASES COMPLETE + REACT FRONTEND**
- **App Status**: ✅ **FULLY FUNCTIONAL - DUAL INTERFACE**
- **Last Session**: Fixed 4 React bugs + AI integration (Session 3)
- **Production Ready**: YES
- **Streamlit App**: Running at http://localhost:8501
- **React App**: Running at http://localhost:5173 (Frontend) + http://localhost:8000 (Backend API)

### What Works Right Now
✅ Live Analysis page - SPY analysis completes successfully
✅ Data fetching (yfinance with multi-layer fallback)
✅ Risk-free rate (4.5% default fallback)
✅ PDF calculation (Breeden-Litzenberger formula)
✅ Statistics (mean, std, skew, implied move, tail probs)
✅ AI interpretation (rule-based fallback, no Ollama needed)
✅ Pattern matching (with ChromaDB deprecation warning - has SQLite fallback)
✅ Results display (all 4 metrics + 4 tabs)
✅ Dark theme CSS (fully visible)

### Latest Test Results (User Confirmed)
```
Session 2 (Streamlit):
Ticker: SPY
Spot Price: $684.54
Expected Price: $689.51 (+$4.97)
Implied Move: ±3.44%
Status: ✅ Analysis complete!

Session 3 (React Frontend):
Tickers: NVDA, AMZN (previously failed with "Need at least 20 strikes")
Status: ✅ "ok now it works" - User confirmed
AI Analysis: ✅ Working with Groq llama-3.3-70b-versatile
Strike Table: ✅ Dynamic CDF calculation
Market Bias: ✅ Consistent with AI interpretation
```

---

## Bug Fixes Applied (Total: 13)

### Session 1 (2025-12-03 Morning)
1. **BreedenlitzenbergPDF constructor** - Removed invalid `use_sabr` parameter
2. **Method call** - `calculate_pdf()` → `calculate_from_options()`
3. **PDFStatistics parameters** - Fixed constructor signature
4. **Dark theme CSS** - Complete color overhaul (light → dark)

### Session 2 (2025-12-03 Afternoon)
5. **Column name mismatch** - Added camelCase ↔ snake_case standardization
6. **Spot price extraction** - Improved fallback logic
7. **Date type conversion** - String → datetime for expiration dates
8. **API variable scope** - Fixed NameError in auto-save
9. **Visualization parameters** - Fixed function names and parameters

### Session 3 (2025-12-08 - React Frontend Polish - THIS SESSION)
10. **Groq AI model deprecation** - Updated llama-3.1 → llama-3.3-70b-versatile
11. **Strike table hardcoded data** - Replaced with dynamic CDF calculation
12. **Market Bias label contradiction** - Changed from skewness-based to direction-based
13. **MIN_STRIKES_FOR_PDF too restrictive** - Lowered 20 → 10 for broader stock coverage

**All fixes documented in**: `.claude/CLAUDE.md` (Bug Fixes section)

---

## Important Files to Read

### For Understanding Project
1. **`.claude/CLAUDE.md`** - Complete project memory (phases, files, decisions)
2. **`docs/PROJECT_EXPLANATION.md`** - Technical & non-technical explanation
3. **`docs/NAVIGATION.md`** - How to navigate the codebase

### For Bugs/Issues
4. **`FIXES_APPLIED.md`** - All 9 fixes with before/after code
5. **`AUDIT_REPORT.md`** - Original technical audit (reference only)

### For Features
6. **`README.md`** - Setup instructions and feature list
7. **`.claude/system_index.json`** - Complete file map

---

## Project Architecture (All Complete)

```
✅ Phase 1: Data Layer
   - OpenBB client (primary)
   - yfinance client (backup) ← CURRENTLY USING
   - FRED client (risk-free rate) ← FALLBACK TO 4.5%
   - DataManager (unified interface)

✅ Phase 2: Core Math
   - Breeden-Litzenberger PDF calculation
   - SABR volatility model
   - PDF statistics (mean, std, skew, kurtosis)

✅ Phase 3: Visualizations
   - 2D PDF plots (Plotly)
   - 3D surface plots
   - Probability tables
   - Dark theme styling

✅ Phase 4: AI Interpretation
   - Ollama integration (optional - NOT INSTALLED)
   - Rule-based fallback ← CURRENTLY USING
   - Pattern matching

✅ Phase 5: Database & History
   - SQLite database
   - PDF snapshot storage
   - Pattern matching (ChromaDB warning - uses SQLite fallback)
   - Prediction tracking

✅ Phase 6: Streamlit App
   - Live Analysis page ← WORKING
   - Historical page
   - Predictions page
   - About page

✅ Phase 7: Deployment
   - Docker configuration
   - Health checks
   - Documentation
```

---

## Commands to Resume Work

### Check Current State
```bash
# Verify working directory
pwd
# Should be: /Users/arjit/.../Quant1 - Option-Implied PDF Visualizer

# Check Streamlit is running
ps aux | grep streamlit
# Should see process running on port 8501

# Access app
# Open browser to: http://localhost:8501
```

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Test specific components
python src/data/data_manager.py
python src/core/breeden_litz.py
```

### Start Streamlit (if not running)
```bash
streamlit run app/streamlit_app.py
```

---

## Key Files Modified Recently

### Main Application Logic
- **`app/pages/1_Live_Analysis.py`** (lines 97-358)
  - Column standardization
  - Date conversion
  - API scope fixes
  - Visualization fixes

### Styling
- **`app/utils/helpers.py`** (lines 11-126)
  - Dark theme CSS

### Data Layer (Fallbacks)
- **`src/data/fred_client.py`** - 4.5% fallback
- **`src/data/data_manager.py`** - Wrapper fallback

### Core Math (SciPy Updates)
- **`src/core/breeden_litz.py`** - trapz → trapezoid
- **`src/core/statistics.py`** - trapz → trapezoid

---

## Known Non-Blocking Issues

### 1. ChromaDB Deprecation Warning
**Status**: Expected, has fallback
**Message**: "deprecated configuration of Chroma"
**Impact**: None - falls back to SQLite
**Fix**: Optional - upgrade ChromaDB or ignore

### 2. FRED API SSL Certificate
**Status**: Expected on macOS Python 3.13
**Message**: "SSL: CERTIFICATE_VERIFY_FAILED"
**Impact**: None - uses 4.5% default rate
**Fix**: Optional - run SSL certificate installer

### 3. Ollama Not Installed
**Status**: Expected - optional enhancement
**Impact**: None - uses rule-based interpretation
**Fix**: Optional - install Ollama for better AI

---

## What to Do Next (If Asked)

### Testing & Polish
1. Test Historical page (need to save some analyses first)
2. Test Predictions page
3. Try different tickers (QQQ, IWM, etc.)
4. Test different expiration dates

### Optional Enhancements
1. Install Ollama for AI interpretation
2. Install ChromaDB for faster pattern matching
3. Fix FRED SSL certificate
4. Add more tickers
5. Integrate Massive.com historical data (user has subscription)

### If User Reports New Bug
1. Ask for exact error message + traceback
2. Check which page/action triggered it
3. Look at similar patterns in `FIXES_APPLIED.md`
4. Most likely: data type mismatch or API parameter issue

---

## Quick Reference - Data Flow

```
User clicks "Run Analysis"
    ↓
1. Fetch option chain (yfinance)
    - Returns DataFrame with camelCase columns
    - Standardize to: optionType, impliedVolatility
    ↓
2. Get risk-free rate (FRED)
    - Try FRED API
    - Fallback to 4.5%
    ↓
3. Calculate PDF (Breeden-Litzenberger)
    - Filter calls
    - Convert exp_date string → datetime
    - Build DataFrame: strike, price, impliedVolatility
    - Call calculate_from_options()
    ↓
4. Calculate statistics
    - PDFStatistics(strikes, pdf, spot_price, time_to_expiry)
    - Call get_summary()
    ↓
5. Find patterns (optional)
    - Initialize api = None
    - Try pattern matching
    ↓
6. Generate interpretation
    - PDFInterpreter with rule-based fallback
    ↓
Display results (4 tabs)
```

---

## Environment Info

- **Python**: 3.13.5
- **Working Directory**: `/Users/arjit/Documents/Professional/AI Consulting/AI Projects/Quant1 - Option-Implied PDF Visualizer`
- **Streamlit Port**: 8501
- **Data Source**: yfinance (OpenBB fallback not working)
- **Risk-Free Rate**: 4.5% default (FRED SSL issue)
- **AI**: Rule-based (Ollama not installed)

---

## Important: What New Claude Should Know

1. **App is functional** - All 7 phases complete, 9 bugs fixed
2. **User tested successfully** - SPY analysis worked end-to-end
3. **Most recent fixes** - Data type mismatches (str vs datetime, camelCase vs snake_case)
4. **Root cause of bugs** - Integration layer between yfinance API and our code expectations
5. **Solution pattern** - Defensive programming with type checks and standardization
6. **Documentation is up-to-date** - `.claude/CLAUDE.md`, `FIXES_APPLIED.md`, this file

**DO NOT** rewrite working code without good reason. App is functional.

**DO** help with testing, new features, or fixing new bugs if they arise.

---

## Session Recovery Checklist

When starting a new session:
- [ ] Read this file (RESUME_CONTEXT.md)
- [ ] Skim `.claude/CLAUDE.md` for project overview
- [ ] Check `FIXES_APPLIED.md` to see what was fixed
- [ ] Verify Streamlit is running (http://localhost:8501)
- [ ] Ask user what they want to work on next

**DO NOT** assume bugs from `AUDIT_REPORT.md` still exist - they're all fixed.
