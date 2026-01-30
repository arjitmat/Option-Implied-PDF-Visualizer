"""
Application constants.
"""

# Default ticker
DEFAULT_TICKER = 'SPY'

# Option chain filtering
MIN_EXPIRY_DAYS = 7
MAX_EXPIRY_DAYS = 90
DEFAULT_EXPIRY_DAYS = 30

# Strike filtering (percentage from spot)
MIN_STRIKE_PCT = 0.80  # 80% of spot price
MAX_STRIKE_PCT = 1.20  # 120% of spot price

# PDF calculation
MIN_STRIKES_FOR_PDF = 10  # Minimum number of strikes needed (reduced for broader stock coverage)
PDF_GRID_POINTS = 500  # Number of points in PDF grid

# SABR parameters
SABR_BETA = 0.5  # CEV exponent (0.5 is common for equity options)
SABR_INITIAL_ALPHA = 0.2
SABR_INITIAL_RHO = -0.3
SABR_INITIAL_NU = 0.3

# Volatility filtering
MIN_IMPLIED_VOL = 0.05  # 5% minimum IV
MAX_IMPLIED_VOL = 2.0   # 200% maximum IV

# FRED series IDs
FRED_SERIES_3M = 'DGS3MO'  # 3-month Treasury
FRED_SERIES_1M = 'DGS1MO'  # 1-month Treasury
FRED_SERIES_6M = 'DGS6MO'  # 6-month Treasury

# Visualization
PLOT_WIDTH = 900
PLOT_HEIGHT = 700
PLOT_COLORSCALE = 'Viridis'
PLOT_BG_COLOR = 'rgb(20,20,20)'

# AI interpretation
MAX_AI_RESPONSE_TOKENS = 500
AI_TEMPERATURE = 0.7

# Historical pattern matching
PATTERN_SIMILARITY_THRESHOLD = 0.85  # Cosine similarity threshold
MAX_HISTORICAL_MATCHES = 5

# Prediction tracking
PREDICTION_EVALUATION_DAYS = 1  # Days after expiration to evaluate prediction
