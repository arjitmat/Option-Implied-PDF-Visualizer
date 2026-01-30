"""
Groq AI client for fast cloud-based inference.

Much faster than local Ollama (responses in <1 second).
Uses llama-3.3-70b-versatile model by default.
"""

import os
from typing import Dict, Optional
import requests


class GroqClient:
    """Client for Groq cloud AI inference."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile"
    ):
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model name (llama-3.3-70b-versatile recommended)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        self._available = None

    def is_available(self) -> bool:
        """
        Check if Groq API is available.

        Returns:
            True if API key is set
        """
        if self._available is not None:
            return self._available

        self._available = bool(self.api_key)
        return self._available

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, any]:
        """
        Generate text using Groq.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with 'response' and metadata

        Raises:
            RuntimeError: If Groq API is not available or request fails
        """
        if not self.is_available():
            raise RuntimeError(
                "Groq API key not found. Set GROQ_API_KEY environment variable. "
                "Get your free API key at: https://console.groq.com/keys"
            )

        try:
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=30  # Groq is fast, 30s is plenty
            )

            response.raise_for_status()
            result = response.json()

            return {
                'response': result['choices'][0]['message']['content'],
                'model': result.get('model', self.model),
                'usage': result.get('usage', {}),
                'finish_reason': result['choices'][0].get('finish_reason')
            }

        except requests.exceptions.Timeout:
            raise RuntimeError("Groq API request timed out")
        except requests.exceptions.RequestException as e:
            error_msg = f"Groq API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\nGroq error details: {error_detail}"
                except:
                    error_msg += f"\nResponse text: {e.response.text[:500]}"
            raise RuntimeError(error_msg)
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected Groq API response format: {str(e)}")


if __name__ == "__main__":
    # Test Groq client
    print("Testing Groq Client...\n")

    client = GroqClient()
    print(f"Groq available: {client.is_available()}")

    if client.is_available():
        try:
            result = client.generate(
                prompt="Explain the Breeden-Litzenberger formula in one sentence.",
                system_prompt="You are a financial mathematics expert.",
                temperature=0.7,
                max_tokens=100
            )

            print("\n" + "="*60)
            print("RESPONSE")
            print("="*60)
            print(f"Model: {result['model']}")
            print(f"\n{result['response']}")
            print("="*60)
            print("\n✅ Groq client test successful!")
        except Exception as e:
            print(f"\n❌ Groq test failed: {str(e)}")
    else:
        print("\n⚠ Groq API key not set. Set GROQ_API_KEY environment variable.")
        print("   Get your free key at: https://console.groq.com/keys")
