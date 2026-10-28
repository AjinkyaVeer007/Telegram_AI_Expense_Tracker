"""LLM instances, created once and shared."""

from langchain_openai import ChatOpenAI

from tracker.config import OPENAI_MODEL
from tracker.models import Transaction

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
structured_llm = llm.with_structured_output(Transaction)
