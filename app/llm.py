import os

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Load environment variables from .env.
load_dotenv()

# Create the shared LLM client.
llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

groq_llm = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

gemini_llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

deepseek_llm = ChatDeepSeek(
    model=os.getenv("DEEPSEEK_MODEL"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)