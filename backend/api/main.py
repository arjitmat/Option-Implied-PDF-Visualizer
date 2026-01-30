"""
FastAPI Backend for Option-Implied PDF Visualizer

Provides REST API endpoints for:
- PDF calculation and analysis
- Market data fetching
- AI interpretation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import os

# Add parent directory to path to import existing modules
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from src.data.data_manager import DataManager
from src.core.breeden_litz import BreedenlitzenbergPDF
from src.core.statistics import PDFStatistics
from src.ai.interpreter import PDFInterpreter
from scipy.stats import norm

# Initialize FastAPI app
app = FastAPI(
    title="Option-Implied PDF Visualizer API",
    description="Real-time probability distribution analysis from option prices",
    version="1.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class AnalysisRequest(BaseModel):
    ticker: str
    days_to_expiry: int = 30
    analysis_mode: str = "standard"
    use_sabr: bool = True

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/api", response_model=HealthResponse)
async def root():
    """API root endpoint - health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/risk-free-rate")
async def get_risk_free_rate():
    """Get current risk-free rate from FRED"""
    try:
        data_manager = DataManager()
        rate = data_manager.get_risk_free_rate()

        return {
            "success": True,
            "data": {
                "rate": float(rate),
                "rate_percent": float(rate * 100)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_options(request: AnalysisRequest):
    """
    Main analysis endpoint - performs full PDF calculation and interpretation

    Args:
        request: AnalysisRequest with ticker, days_to_expiry, analysis_mode, use_sabr

    Returns:
        Complete analysis results including PDF, statistics, and AI interpretation
    """
    try:
        # Initialize data manager
        data_manager = DataManager()

        # Try increasingly wider date ranges to get sufficient data
        options_df = None
        actual_dte = request.days_to_expiry

        # Strategy 1: Try exact date matching first
        try:
            all_expirations = data_manager.get_expirations(ticker=request.ticker)

            # Find the expiration closest to requested DTE
            target_date = datetime.now() + timedelta(days=request.days_to_expiry)

            closest_exp = None
            min_diff = float('inf')

            for exp_str in all_expirations:
                exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    closest_exp = exp_str

            if closest_exp:
                # Calculate actual DTE for the closest expiration
                closest_date = datetime.strptime(closest_exp, '%Y-%m-%d')
                actual_dte = (closest_date - datetime.now()).days

                # Fetch options for the closest expiration (with small window)
                options_df = data_manager.get_options(
                    ticker=request.ticker,
                    min_expiry_days=max(1, actual_dte - 2),
                    max_expiry_days=actual_dte + 2
                )
        except Exception as exp_error:
            print(f"Exact matching failed: {exp_error}")

        # Strategy 2: If not enough data, try wider range
        if options_df is None or len(options_df) < 20:
            print(f"Trying wider date range for {request.ticker}...")
            try:
                options_df = data_manager.get_options(
                    ticker=request.ticker,
                    min_expiry_days=max(1, request.days_to_expiry - 15),
                    max_expiry_days=request.days_to_expiry + 15
                )
            except Exception as wide_error:
                print(f"Wide range failed: {wide_error}")

        # Strategy 3: If still not enough, try very wide range
        if options_df is None or len(options_df) < 20:
            print(f"Trying very wide date range for {request.ticker}...")
            try:
                options_df = data_manager.get_options(
                    ticker=request.ticker,
                    min_expiry_days=7,
                    max_expiry_days=90
                )
            except Exception as final_error:
                print(f"Final attempt failed: {final_error}")

        # Final check: Do we have any data?
        if options_df is None or options_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No option data found for {request.ticker}. The ticker may not have active options, or data providers may be unavailable."
            )

        # Log how much data we got
        print(f"Fetched {len(options_df)} total option contracts for {request.ticker}")

        # Get risk-free rate
        risk_free_rate = data_manager.get_risk_free_rate()

        # Get spot price
        if 'underlying_price' in options_df.columns:
            spot_price = float(options_df['underlying_price'].iloc[0])
        else:
            try:
                spot_price = float(data_manager.get_spot_price(request.ticker))
            except:
                spot_price = float(options_df['strike'].median())

        # Standardize column names
        if 'optionType' not in options_df.columns and 'option_type' in options_df.columns:
            options_df = options_df.rename(columns={'option_type': 'optionType'})
        if 'impliedVolatility' not in options_df.columns and 'implied_volatility' in options_df.columns:
            options_df = options_df.rename(columns={'implied_volatility': 'impliedVolatility'})

        # Filter for calls
        calls = options_df[options_df['optionType'] == 'call'].copy()

        if calls.empty:
            raise HTTPException(status_code=404, detail="No call options found")

        # Calculate time to expiry
        exp_date = calls['expiration'].iloc[0]
        if isinstance(exp_date, str):
            exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
        days_to_exp = (exp_date - datetime.now()).days
        T = days_to_exp / 365.0

        # Prepare PDF input
        pdf_input = calls[['strike', 'impliedVolatility']].copy()

        # Add price column
        if 'bid' in calls.columns and 'ask' in calls.columns:
            pdf_input['price'] = (calls['bid'] + calls['ask']) / 2
        elif 'lastPrice' in calls.columns:
            pdf_input['price'] = calls['lastPrice']
        else:
            # Black-Scholes fallback
            sigma = pdf_input['impliedVolatility'].values
            K = pdf_input['strike'].values
            d1 = (np.log(spot_price / K) + (risk_free_rate + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            pdf_input['price'] = spot_price * norm.cdf(d1) - K * np.exp(-risk_free_rate * T) * norm.cdf(d2)

        # Calculate PDF
        pdf_calculator = BreedenlitzenbergPDF()
        interpolation_method = 'sabr' if request.use_sabr else 'spline'

        print(f"Calculating PDF with {len(pdf_input)} call options (strikes: {pdf_input['strike'].min():.2f} - {pdf_input['strike'].max():.2f})")

        try:
            pdf_strikes, pdf_values = pdf_calculator.calculate_from_options(
                options_df=pdf_input,
                spot_price=spot_price,
                risk_free_rate=risk_free_rate,
                time_to_expiry=T,
                option_type='call',
                interpolation_method=interpolation_method
            )
        except ValueError as ve:
            # Better error message for insufficient strikes
            error_msg = str(ve)
            if "Need at least" in error_msg:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient option data for {request.ticker}. {error_msg}. Try selecting a different ticker or wait a few moments for data to refresh."
                )
            raise HTTPException(status_code=400, detail=error_msg)

        # Calculate statistics
        stats_calc = PDFStatistics(
            strikes=pdf_strikes,
            pdf=pdf_values,
            spot_price=spot_price,
            time_to_expiry=T
        )
        statistics = stats_calc.get_summary()

        # AI Interpretation
        interpreter = PDFInterpreter(mode=request.analysis_mode)
        interp_result = interpreter.interpret_single_pdf(
            ticker=request.ticker,
            spot=spot_price,
            stats=statistics,
            days_to_expiry=days_to_exp,
            historical_matches=None
        )

        # Prepare response data
        response_data = {
            "ticker": request.ticker,
            "spot_price": float(spot_price),
            "risk_free_rate": float(risk_free_rate),
            "days_to_expiry": int(days_to_exp),
            "time_to_expiry": float(T),
            "pdf": {
                "strikes": pdf_strikes.tolist(),
                "values": pdf_values.tolist()
            },
            "statistics": {
                "mean": float(statistics.get('mean', 0)),
                "std_dev": float(statistics.get('std_dev', 0)),
                "skewness": float(statistics.get('skewness', 0)),
                "kurtosis": float(statistics.get('kurtosis', 0)),
                "implied_move_pct": float(statistics.get('implied_move_pct', 0)),
                "ci_lower": float(statistics.get('ci_lower', 0)),
                "ci_upper": float(statistics.get('ci_upper', 0)),
                "tail_prob_down_10pct": float(statistics.get('tail_prob_down_10pct', 0)),
                "tail_prob_up_10pct": float(statistics.get('tail_prob_up_10pct', 0))
            },
            "interpretation": interp_result.get('interpretation', ''),
            "analysis_mode": request.analysis_mode,
            "interpolation_method": interpolation_method
        }

        return {
            "success": True,
            "data": response_data,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/api/tickers")
async def get_supported_tickers():
    """Get list of commonly supported tickers"""
    return {
        "success": True,
        "data": {
            "etfs": ["SPY", "QQQ", "IWM", "DIA", "EEM", "GLD", "SLV", "TLT"],
            "mega_cap": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"],
            "popular": ["AMD", "NFLX", "BABA", "DIS", "BA", "JPM", "GS"]
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/chart/{ticker}")
async def get_chart_data(ticker: str, interval: str = "1h", range: str = "1d"):
    """
    Proxy endpoint for Yahoo Finance chart data (avoids CORS issues)
    Uses yfinance library which handles authentication properly

    Args:
        ticker: Stock ticker symbol (e.g., SPY, AAPL)
        interval: Chart interval (1m, 5m, 15m, 1h, 1d, etc.)
        range: Chart range (1d, 5d, 1mo, 1y, etc.)

    Returns:
        Chart data with timestamps and prices
    """
    try:
        import yfinance as yf
        import pandas as pd

        # Map range to period for yfinance
        period_map = {
            '1d': '1d',
            '5d': '5d',
            '1mo': '1mo',
            '1y': '1y'
        }
        period = period_map.get(range, '1d')

        # Fetch data using yfinance
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period=period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        # Convert to list of {timestamp, price} objects
        chart_points = []
        for timestamp, row in hist.iterrows():
            chart_points.append({
                "timestamp": int(timestamp.timestamp()),
                "price": float(row['Close'])
            })

        return {
            "success": True,
            "data": {
                "ticker": ticker,
                "interval": interval,
                "range": range,
                "points": chart_points,
                "count": len(chart_points)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "success": False,
        "data": None,
        "error": "Endpoint not found",
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "success": False,
        "data": None,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup"""
    print("=" * 80)
    print("🚀 Option-Implied PDF Visualizer API Starting...")
    print("=" * 80)
    print("📊 Endpoints available:")
    print("  - GET  /                    (Health check)")
    print("  - GET  /api/health          (Health check)")
    print("  - GET  /api/risk-free-rate  (Current risk-free rate)")
    print("  - POST /api/analyze         (Run PDF analysis)")
    print("  - GET  /api/tickers         (Supported tickers)")
    print("  - GET  /api/chart/{ticker}  (Price chart data)")
    print("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    print("\n" + "=" * 80)
    print("🛑 Option-Implied PDF Visualizer API Shutting Down...")
    print("=" * 80)

# =============================================================================
# SERVE REACT FRONTEND (for Docker/Production deployment)
# =============================================================================

# Check if static files exist (built React app)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    print(f"📦 Static files found at: {static_dir}")
    print(f"📂 Contents: {list(static_dir.iterdir())}")

    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    # Serve index.html for root and all non-API routes
    @app.get("/")
    async def serve_root():
        """Serve React app at root"""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            return {"error": "Frontend build not found", "path": str(index_file)}

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React frontend for all non-API routes (SPA routing)"""
        # Don't intercept API routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # Check if requesting a static file
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for SPA routing
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
else:
    print(f"⚠️  No static files found at: {static_dir}")
    print(f"⚠️  React frontend will not be served!")

    @app.get("/")
    async def no_frontend():
        """Fallback when no frontend is built"""
        return {
            "message": "React frontend not built",
            "api_docs": "/docs",
            "health": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
