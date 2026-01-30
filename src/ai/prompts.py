"""
Prompt templates for AI interpretation of option-implied PDFs.
"""

from typing import Dict, List, Optional
from datetime import datetime


PDF_ANALYSIS_PROMPT = """You are a derivatives analyst interpreting option-implied probability densities for institutional clients.

Current Market Context:
- Ticker: {ticker}
- Spot Price: ${spot:.2f}
- Analysis Date: {date}
- Days to Expiration: {days_to_expiry}

PDF Statistics:
- Expected Price (Mean): ${mean:.2f} ({drift:+.2f}% from spot)
- Standard Deviation: ${std:.2f}
- Implied Move: ±{implied_move:.2f}%
- Implied Volatility: {implied_vol:.2f}%

Distribution Shape:
- Skewness: {skew:.3f} (negative = left tail heavy, positive = right tail heavy)
- Excess Kurtosis: {kurtosis:.3f} (positive = fat tails, negative = thin tails)

Tail Risk Analysis:
- P(Down >5%): {prob_down_5:.2f}%
- P(Up >5%): {prob_up_5:.2f}%
- P(Down >10%): {prob_down_10:.2f}%
- P(Up >10%): {prob_up_10:.2f}%

Confidence Intervals:
- 68% CI: ${ci_68_lower:.2f} - ${ci_68_upper:.2f}
- 95% CI: ${ci_95_lower:.2f} - ${ci_95_upper:.2f}

{historical_context}

Provide a comprehensive analysis covering:

1. Market Sentiment (2-3 sentences)
   - What does the PDF shape reveal about current market positioning?
   - Is there directional bias or are markets balanced?

2. Tail Risk Assessment (2-3 sentences)
   - Compare tail probabilities to a normal distribution
   - Are extreme moves priced in or underpriced?
   - What does the skewness/kurtosis tell us?

3. Trading Implications (2-3 sentences)
   - What strategies are favored by this probability distribution?
   - Where are the areas of mispricing or opportunity?

{historical_comparison}

4. Key Takeaway (1 sentence)
   - Single most important insight for traders

Be specific and quantitative. Reference the actual statistics provided. No generic fluff.
"""


HISTORICAL_COMPARISON_PROMPT = """
Historical Pattern Match:
The current PDF shape is {similarity:.1f}% similar to {match_date}, when:
- Market conditions: {match_description}
- Subsequent move: {actual_move}
- Prediction accuracy: {accuracy}

Consider this historical precedent in your analysis.
"""


MULTI_EXPIRATION_PROMPT = """You are analyzing the term structure of option-implied probabilities across multiple expirations.

Market: {ticker} @ ${spot:.2f}
Analysis Date: {date}

Expiration Structure:
{expiration_data}

Term Structure Observations:
- Volatility term structure: {vol_term_structure}
- Skew evolution: {skew_evolution}
- Tail risk progression: {tail_evolution}

Analyze:

1. Term Structure Pattern (2-3 sentences)
   - How does implied volatility change across time?
   - What does this reveal about market expectations?

2. Risk Evolution (2-3 sentences)
   - How do tail risks evolve with time?
   - Are near-term or longer-term expirations pricing more risk?

3. Structural Insights (2-3 sentences)
   - Any anomalies or dislocations in the term structure?
   - What trading opportunities does this create?

4. Summary (1 sentence)
   - Key insight from the term structure analysis

Be concise and quantitative.
"""


PREDICTION_TRACKING_PROMPT = """You are evaluating the accuracy of a past probability forecast.

Original Forecast ({forecast_date}):
- Predicted probability: {predicted_prob:.2f}%
- Condition: {condition}
- Target level: ${target_level:.2f}
- Expiration: {expiration_date}

Actual Outcome ({evaluation_date}):
- Final price: ${final_price:.2f}
- Condition met: {outcome}
- Prediction accuracy: {accuracy}

Provide a brief assessment (3-4 sentences):
1. Was the forecast directionally correct?
2. What factors may have contributed to accuracy/inaccuracy?
3. What can we learn for future forecasts?

Be honest and analytical.
"""


def format_pdf_analysis_prompt(
    ticker: str,
    spot: float,
    stats: Dict[str, float],
    days_to_expiry: int,
    historical_matches: Optional[List[Dict]] = None
) -> str:
    """
    Format the main PDF analysis prompt.

    Args:
        ticker: Ticker symbol
        spot: Current spot price
        stats: PDF statistics dictionary
        days_to_expiry: Days to expiration
        historical_matches: Optional list of historical pattern matches

    Returns:
        Formatted prompt string
    """
    # Format historical context
    historical_context = ""
    if historical_matches and len(historical_matches) > 0:
        historical_context = "Historical Pattern Matches:\n"
        for i, match in enumerate(historical_matches[:3], 1):
            historical_context += f"{i}. {match['date']}: {match['similarity']:.0f}% similar - {match['description']}\n"
    else:
        historical_context = "No significant historical pattern matches found."

    # Format historical comparison
    historical_comparison = ""
    if historical_matches and len(historical_matches) > 0:
        best_match = historical_matches[0]
        historical_comparison = HISTORICAL_COMPARISON_PROMPT.format(
            similarity=best_match['similarity'] * 100,
            match_date=best_match['date'],
            match_description=best_match.get('description', 'N/A'),
            actual_move=best_match.get('actual_move', 'N/A'),
            accuracy=best_match.get('accuracy', 'N/A')
        )

    # Format main prompt
    return PDF_ANALYSIS_PROMPT.format(
        ticker=ticker,
        spot=spot,
        date=datetime.now().strftime('%Y-%m-%d'),
        days_to_expiry=days_to_expiry,
        mean=stats['mean'],
        drift=stats.get('risk_neutral_drift_pct', 0),
        std=stats['std'],
        implied_move=stats['implied_move_pct'],
        implied_vol=stats['implied_volatility'] * 100,
        skew=stats['skewness'],
        kurtosis=stats['excess_kurtosis'],
        prob_down_5=stats['prob_down_5pct'] * 100,
        prob_up_5=stats['prob_up_5pct'] * 100,
        prob_down_10=stats['prob_down_10pct'] * 100,
        prob_up_10=stats['prob_up_10pct'] * 100,
        ci_68_lower=stats['ci_68_lower'],
        ci_68_upper=stats['ci_68_upper'],
        ci_95_lower=stats['ci_95_lower'],
        ci_95_upper=stats['ci_95_upper'],
        historical_context=historical_context,
        historical_comparison=historical_comparison
    )


def format_multi_expiration_prompt(
    ticker: str,
    spot: float,
    expiration_data: List[Dict[str, any]]
) -> str:
    """
    Format multi-expiration analysis prompt.

    Args:
        ticker: Ticker symbol
        spot: Current spot price
        expiration_data: List of dicts with stats for each expiration

    Returns:
        Formatted prompt string
    """
    # Format expiration data table
    exp_table = ""
    vols = []
    skews = []
    for exp in expiration_data:
        days = exp['days_to_expiry']
        stats = exp['stats']
        exp_table += f"  {days}D: IV={stats['implied_volatility']*100:.1f}%, "
        exp_table += f"Skew={stats['skewness']:.2f}, "
        exp_table += f"Move=±{stats['implied_move_pct']:.1f}%\n"

        vols.append(stats['implied_volatility'] * 100)
        skews.append(stats['skewness'])

    # Analyze term structure patterns
    if len(vols) >= 2:
        vol_trend = "upward" if vols[-1] > vols[0] else "downward" if vols[-1] < vols[0] else "flat"
        vol_term_structure = f"{vol_trend} ({vols[0]:.1f}% → {vols[-1]:.1f}%)"
    else:
        vol_term_structure = "insufficient data"

    if len(skews) >= 2:
        skew_trend = "increasing" if skews[-1] > skews[0] else "decreasing"
        skew_evolution = f"{skew_trend} ({skews[0]:.2f} → {skews[-1]:.2f})"
    else:
        skew_evolution = "insufficient data"

    # Tail risk evolution
    near_term_down = expiration_data[0]['stats']['prob_down_5pct'] * 100
    far_term_down = expiration_data[-1]['stats']['prob_down_5pct'] * 100
    tail_evolution = f"5% down risk: {near_term_down:.1f}% (near) → {far_term_down:.1f}% (far)"

    return MULTI_EXPIRATION_PROMPT.format(
        ticker=ticker,
        spot=spot,
        date=datetime.now().strftime('%Y-%m-%d'),
        expiration_data=exp_table,
        vol_term_structure=vol_term_structure,
        skew_evolution=skew_evolution,
        tail_evolution=tail_evolution
    )


def format_prediction_tracking_prompt(
    forecast_date: str,
    predicted_prob: float,
    condition: str,
    target_level: float,
    expiration_date: str,
    evaluation_date: str,
    final_price: float,
    outcome: bool
) -> str:
    """
    Format prediction tracking evaluation prompt.

    Args:
        forecast_date: Date when forecast was made
        predicted_prob: Predicted probability (0-1)
        condition: Condition type ('above' or 'below')
        target_level: Target price level
        expiration_date: Original expiration date
        evaluation_date: Date of evaluation
        final_price: Actual final price
        outcome: Whether condition was met

    Returns:
        Formatted prompt string
    """
    accuracy = "Correct" if (
        (condition == 'above' and final_price > target_level and predicted_prob > 0.5) or
        (condition == 'below' and final_price < target_level and predicted_prob > 0.5) or
        (condition == 'above' and final_price <= target_level and predicted_prob <= 0.5) or
        (condition == 'below' and final_price >= target_level and predicted_prob <= 0.5)
    ) else "Incorrect"

    return PREDICTION_TRACKING_PROMPT.format(
        forecast_date=forecast_date,
        predicted_prob=predicted_prob * 100,
        condition=f"Price {condition} ${target_level:.2f}",
        target_level=target_level,
        expiration_date=expiration_date,
        evaluation_date=evaluation_date,
        final_price=final_price,
        outcome="Yes" if outcome else "No",
        accuracy=accuracy
    )


# System prompts for different analysis modes
SYSTEM_PROMPTS = {
    'standard': "You are an expert derivatives analyst specializing in option-implied probability analysis. Provide clear, quantitative insights.",
    'conservative': "You are a risk-focused derivatives analyst. Emphasize downside protection and tail risk management.",
    'aggressive': "You are a returns-focused derivatives analyst. Identify asymmetric opportunities and mispriced volatility.",
    'educational': "You are a derivatives educator. Explain concepts clearly while maintaining analytical rigor."
}


if __name__ == "__main__":
    # Test prompt formatting
    print("Testing prompt templates...\n")

    # Sample statistics
    stats = {
        'mean': 451.5,
        'std': 15.2,
        'implied_move_pct': 3.38,
        'implied_volatility': 0.20,
        'skewness': -0.15,
        'excess_kurtosis': 0.5,
        'prob_down_5pct': 0.18,
        'prob_up_5pct': 0.22,
        'prob_down_10pct': 0.08,
        'prob_up_10pct': 0.10,
        'ci_68_lower': 436.3,
        'ci_68_upper': 466.7,
        'ci_95_lower': 421.1,
        'ci_95_upper': 481.9,
        'risk_neutral_drift_pct': 0.3
    }

    # Test main analysis prompt
    prompt = format_pdf_analysis_prompt(
        ticker="SPY",
        spot=450.0,
        stats=stats,
        days_to_expiry=30,
        historical_matches=[{
            'date': '2023-10-15',
            'similarity': 0.85,
            'description': 'Pre-earnings uncertainty',
            'actual_move': '-2.5%',
            'accuracy': 'High'
        }]
    )

    print("=== PDF Analysis Prompt ===")
    print(prompt[:500] + "...\n")

    # Test multi-expiration prompt
    exp_data = [
        {'days_to_expiry': 15, 'stats': stats},
        {'days_to_expiry': 30, 'stats': stats},
        {'days_to_expiry': 60, 'stats': stats}
    ]

    prompt2 = format_multi_expiration_prompt("SPY", 450.0, exp_data)
    print("=== Multi-Expiration Prompt ===")
    print(prompt2[:300] + "...\n")

    print("✅ Prompt template test passed!")
