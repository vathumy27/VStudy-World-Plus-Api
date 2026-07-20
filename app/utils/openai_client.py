import os

from flask import current_app


class OpenAIClient:
    """OpenAI API client wrapper with mock fallback."""

    @staticmethod
    def is_configured():
        """Return True if a real OpenAI API key is configured."""
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return False
        placeholders = {"your-openai-api-key", "changeme", "none", "null"}
        return api_key.lower() not in placeholders

    @staticmethod
    def generate_text(prompt, system_message=None, max_tokens=500):
        """
        Generate text using OpenAI API when configured,
        otherwise return None to trigger mock fallback.
        """
        if not OpenAIClient.is_configured():
            return None

        api_key = os.getenv("OPENAI_API_KEY", "").strip()

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, timeout=25.0)
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.4,
            )
            content = response.choices[0].message.content
            return content.strip() if content else None
        except Exception as exc:
            try:
                current_app.logger.error("OpenAI API error: %s", str(exc))
            except Exception:
                pass
            return None
