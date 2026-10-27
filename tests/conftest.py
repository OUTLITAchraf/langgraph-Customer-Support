
import os

# Provide placeholder configuration for tests that use mocked clients.
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-deepseek-key")

os.environ.setdefault("OPENROUTER_MODEL", "test-model")
os.environ.setdefault("GROQ_MODEL", "test-model")
os.environ.setdefault("GEMINI_MODEL", "gemini-3.5-flash-lite")
os.environ.setdefault("DEEPSEEK_MODEL", "test-model")

os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "")
os.environ.setdefault("LANGFUSE_BASE_URL", "http://localhost:3000")
