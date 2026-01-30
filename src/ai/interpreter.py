"""
AI interpretation engine for option-implied PDFs.

Uses Groq cloud API for fast inference (Llama 3.1 by default).
Falls back to Ollama if Groq unavailable.
"""

import os
from typing import Dict, List, Optional
import json
from datetime import datetime

from config.settings import GROQ_API_KEY, GROQ_MODEL, OLLAMA_MODEL, OLLAMA_HOST
from src.ai.prompts import (
    format_pdf_analysis_prompt,
    format_multi_expiration_prompt,
    format_prediction_tracking_prompt,
    SYSTEM_PROMPTS
)
from src.ai.groq_client import GroqClient


class OllamaClient:
    """Client for Ollama local LLM inference."""

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        host: str = OLLAMA_HOST
    ):
        """
        Initialize Ollama client.

        Args:
            model: Model name (e.g., 'qwen3:7b')
            host: Ollama server host URL
        """
        self.model = model
        self.host = host
        self._available = None

    def is_available(self) -> bool:
        """
        Check if Ollama is available.

        Returns:
            True if Ollama is running and model is available
        """
        if self._available is not None:
            return self._available

        try:
            import requests
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                self._available = any(self.model in name for name in model_names)
                return self._available
            return False
        except Exception as e:
            print(f"Ollama not available: {str(e)}")
            self._available = False
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, any]:
        """
        Generate text using Ollama.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with 'response' and metadata

        Raises:
            RuntimeError: If Ollama is not available
        """
        if not self.is_available():
            raise RuntimeError(
                f"Ollama is not available. Please install Ollama and pull the {self.model} model. "
                "Visit: https://ollama.ai/download"
            )

        try:
            import requests

            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens
                }
            }

            if system_prompt:
                payload['system'] = system_prompt

            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            return {
                'response': result.get('response', ''),
                'model': result.get('model', self.model),
                'total_duration': result.get('total_duration', 0),
                'eval_count': result.get('eval_count', 0)
            }

        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")


class PDFInterpreter:
    """
    Interpreter for option-implied probability density functions.

    Generates human-readable analysis using AI.
    Uses Groq (fast cloud) first, falls back to Ollama (local) if unavailable.
    """

    def __init__(
        self,
        mode: str = 'standard',
        use_groq: bool = True
    ):
        """
        Initialize PDF interpreter.

        Args:
            mode: Analysis mode ('standard', 'conservative', 'aggressive', 'educational')
            use_groq: Try Groq first (recommended for speed)
        """
        self.mode = mode
        self.system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS['standard'])

        # Try Groq first (much faster), then Ollama
        self.groq_client = GroqClient(model=GROQ_MODEL) if use_groq else None
        self.ollama_client = OllamaClient(model=OLLAMA_MODEL)

        # Determine which client to use
        if self.groq_client and self.groq_client.is_available():
            self.client = self.groq_client
            self.client_name = "Groq"
        elif self.ollama_client.is_available():
            self.client = self.ollama_client
            self.client_name = "Ollama"
        else:
            self.client = None
            self.client_name = "None"

    def interpret_single_pdf(
        self,
        ticker: str,
        spot: float,
        stats: Dict[str, float],
        days_to_expiry: int,
        historical_matches: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """
        Interpret a single PDF.

        Args:
            ticker: Ticker symbol
            spot: Current spot price
            stats: PDF statistics dictionary
            days_to_expiry: Days to expiration
            historical_matches: Optional historical pattern matches

        Returns:
            Dictionary with interpretation and metadata
        """
        # Format prompt
        prompt = format_pdf_analysis_prompt(
            ticker=ticker,
            spot=spot,
            stats=stats,
            days_to_expiry=days_to_expiry,
            historical_matches=historical_matches
        )

        # Generate interpretation
        try:
            if not self.client:
                raise RuntimeError("No AI client available (neither Groq nor Ollama)")

            print(f"[AI DEBUG] Using {self.client_name} for generation")

            result = self.client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.7,
                max_tokens=500
            )

            print(f"[AI DEBUG] ✅ {self.client_name} generation successful! Response length: {len(result['response'])} chars")

            return {
                'interpretation': result['response'],
                'ticker': ticker,
                'spot': spot,
                'days_to_expiry': days_to_expiry,
                'timestamp': datetime.now().isoformat(),
                'model': result.get('model'),
                'client': self.client_name,
                'stats': stats,
                'historical_matches': historical_matches or [],
                'mode': self.mode
            }

        except Exception as e:
            # Return fallback interpretation if AI not available
            print(f"[AI DEBUG] ❌ AI generation FAILED: {str(e)}")
            print(f"[AI DEBUG] Using statistical fallback")
            return {
                'interpretation': self._fallback_interpretation(stats, spot),
                'ticker': ticker,
                'spot': spot,
                'days_to_expiry': days_to_expiry,
                'timestamp': datetime.now().isoformat(),
                'model': 'fallback',
                'client': 'fallback',
                'stats': stats,
                'historical_matches': historical_matches or [],
                'mode': 'fallback',
                'error': str(e)
            }

    def interpret_multi_expiration(
        self,
        ticker: str,
        spot: float,
        expiration_data: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Interpret multiple expirations (term structure analysis).

        Args:
            ticker: Ticker symbol
            spot: Current spot price
            expiration_data: List of dicts with stats for each expiration

        Returns:
            Dictionary with interpretation and metadata
        """
        # Format prompt
        prompt = format_multi_expiration_prompt(
            ticker=ticker,
            spot=spot,
            expiration_data=expiration_data
        )

        # Generate interpretation
        try:
            result = self.client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.7,
                max_tokens=400
            )

            return {
                'interpretation': result['response'],
                'ticker': ticker,
                'spot': spot,
                'timestamp': datetime.now().isoformat(),
                'model': result.get('model'),
                'expiration_data': expiration_data,
                'mode': self.mode
            }

        except RuntimeError as e:
            return {
                'interpretation': self._fallback_multi_expiration(expiration_data),
                'ticker': ticker,
                'spot': spot,
                'timestamp': datetime.now().isoformat(),
                'model': 'fallback',
                'expiration_data': expiration_data,
                'mode': 'fallback',
                'error': str(e)
            }

    def _fallback_interpretation(
        self,
        stats: Dict[str, float],
        spot: float
    ) -> str:
        """
        Generate fallback interpretation when AI is unavailable.

        Args:
            stats: PDF statistics
            spot: Spot price

        Returns:
            Basic interpretation string
        """
        lines = []
        lines.append("**Market Sentiment:**")

        # Directional bias
        drift = stats.get('risk_neutral_drift_pct', 0)
        if abs(drift) < 0.5:
            lines.append(f"Market is balanced around current levels (${spot:.2f}).")
        elif drift > 0:
            lines.append(f"Slight bullish bias with mean at ${stats['mean']:.2f} (+{drift:.1f}%).")
        else:
            lines.append(f"Slight bearish bias with mean at ${stats['mean']:.2f} ({drift:.1f}%).")

        # Volatility
        impl_move = stats['implied_move_pct']
        lines.append(f"Implied move of ±{impl_move:.2f}% suggests {'elevated' if impl_move > 3 else 'moderate'} volatility expectations.")

        lines.append("\n**Tail Risk:**")

        # Skewness
        skew = stats['skewness']
        if skew < -0.3:
            lines.append("Significant negative skew indicates heightened crash risk concerns.")
        elif skew > 0.3:
            lines.append("Positive skew suggests markets pricing more upside potential.")
        else:
            lines.append("Relatively symmetric distribution with balanced tail risks.")

        # Kurtosis
        kurt = stats['excess_kurtosis']
        if kurt > 0.5:
            lines.append(f"Fat tails (kurtosis={kurt:.2f}) indicate higher probability of extreme moves than normal distribution.")
        else:
            lines.append("Tail risks appear in line with normal distribution expectations.")

        lines.append("\n**Key Takeaway:**")

        # Summary
        if skew < -0.3 and kurt > 0.5:
            lines.append("Markets pricing significant downside risk with elevated crash probability.")
        elif impl_move > 4:
            lines.append("High volatility regime - expect large price swings in either direction.")
        elif abs(drift) < 0.5 and abs(skew) < 0.2:
            lines.append("Balanced market with no clear directional bias or tail risk premium.")
        else:
            lines.append(f"Moderate volatility environment with {'bearish' if drift < 0 else 'bullish'} lean.")

        lines.append("\n*(AI interpretation unavailable - using fallback analysis)*")

        return "\n".join(lines)

    def _fallback_multi_expiration(
        self,
        expiration_data: List[Dict[str, any]]
    ) -> str:
        """Generate fallback multi-expiration analysis."""
        lines = []
        lines.append("**Term Structure Analysis:**")

        # Extract volatilities
        vols = [exp['stats']['implied_volatility'] * 100 for exp in expiration_data]
        days = [exp['days_to_expiry'] for exp in expiration_data]

        # Vol term structure
        if vols[-1] > vols[0] * 1.1:
            lines.append(f"Upward sloping volatility term structure ({vols[0]:.1f}% → {vols[-1]:.1f}%), indicating increasing uncertainty over time.")
        elif vols[-1] < vols[0] * 0.9:
            lines.append(f"Inverted volatility term structure ({vols[0]:.1f}% → {vols[-1]:.1f}%), suggesting near-term event risk.")
        else:
            lines.append(f"Relatively flat volatility term structure ({vols[0]:.1f}% to {vols[-1]:.1f}%).")

        # Skew evolution
        skews = [exp['stats']['skewness'] for exp in expiration_data]
        if abs(skews[-1]) > abs(skews[0]) * 1.2:
            lines.append("Skew increases with time, suggesting growing tail risk concerns for longer horizons.")
        else:
            lines.append("Consistent skew across expirations indicates stable risk perception.")

        lines.append("\n*(AI interpretation unavailable - using fallback analysis)*")

        return "\n".join(lines)


if __name__ == "__main__":
    # Test interpreter
    print("Testing PDF Interpreter...\n")

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

    # Initialize interpreter
    interpreter = PDFInterpreter(mode='standard')

    # Check if Ollama is available
    print(f"Ollama available: {interpreter.client.is_available()}")

    # Interpret (will use fallback if Ollama not available)
    result = interpreter.interpret_single_pdf(
        ticker="SPY",
        spot=450.0,
        stats=stats,
        days_to_expiry=30
    )

    print("\n" + "="*60)
    print("INTERPRETATION RESULT")
    print("="*60)
    print(f"Model: {result['model']}")
    print(f"Mode: {result['mode']}")
    print(f"\n{result['interpretation']}")
    print("="*60)

    print("\n✅ PDF Interpreter test completed!")
    if result['model'] == 'fallback':
        print("   Note: Using fallback interpretation (Ollama not available)")
        print("   Install Ollama from https://ollama.ai to enable AI interpretation")
