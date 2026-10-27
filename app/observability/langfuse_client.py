import os

from dotenv import load_dotenv
from langfuse import get_client

# Load environment variables from the project root.
load_dotenv()

# Support both current and legacy Langfuse host variable names.
if not os.getenv("LANGFUSE_BASE_URL"):
    base_url = os.getenv("LANGFUSE_HOST")

    if base_url:
        os.environ["LANGFUSE_BASE_URL"] = base_url

# Create the Langfuse client using environment variables.
langfuse = get_client()