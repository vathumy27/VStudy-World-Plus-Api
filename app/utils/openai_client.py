import os

from flask import current_app


class OpenAIClient:
    """OpenAI API client wrapper with mock fallback."""

    @staticmethod
    def is_configured():
        """Return True if OpenAI API key is configured."""
        return bool(os.getenv("OPENAI_API_KEY", "").strip())

    @staticmethod
    def generate_text(prompt, system_message=None, max_tokens=500):
        """
        Generate text using OpenAI API when configured,
        otherwise return None to trigger mock fallback.
        """
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return None

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            current_app.logger.error("OpenAI API error: %s", str(exc))
            return None
