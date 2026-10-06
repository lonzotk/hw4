import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import ChatDeps, ChatReply
from tools import lookup_product_description, lookup_product_price, lookup_product_stock, lookup_products
from audit import record_step

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
PROMPT = (Path(__file__).parent / "prompts" / "prompt.md").read_text(encoding="utf-8")


def build_agent() -> Agent:
    portkey_key = os.getenv("PORTKEY_API_KEY")
    model_name = os.getenv("PORTKEY_MODEL")
    provider_name = os.getenv("PORTKEY_PROVIDER")
    if not portkey_key or not model_name or not provider_name:
        raise RuntimeError("PORTKEY_API_KEY, PORTKEY_MODEL, and PORTKEY_PROVIDER must be set in the Homework 4 .env file.")
    client = AsyncOpenAI(api_key=portkey_key, base_url="https://api.portkey.ai/v1", default_headers={"x-portkey-api-key": portkey_key, "x-portkey-provider": provider_name})
    provider = OpenAIProvider(openai_client=client)
    return Agent(OpenAIChatModel(model_name, provider=provider), deps_type=ChatDeps, output_type=ChatReply, system_prompt=PROMPT, tools=[lookup_products, lookup_product_description, lookup_product_price, lookup_product_stock, customer_context])


def customer_context(ctx: RunContext[ChatDeps]) -> str:
    """Return safe identity, page context, and recent chat history for this request."""
    identity = "Guest shopper"
    if ctx.deps.customer_name and ctx.deps.customer_email:
        identity = f"Logged-in customer: {ctx.deps.customer_name} ({ctx.deps.customer_email})"
    history = "\n".join(f"{item.role}: {item.content}" for item in ctx.deps.history[-10:]) or "No previous messages."
    record_step("customer_context", {"customer": "authenticated" if ctx.deps.customer_email else "guest", "page_context": ctx.deps.page_context or "none"}, "safe context provided")
    return f"{identity}\nCurrent page context: {ctx.deps.page_context or 'None'}\nRecent history:\n{history}"


sales_agent = build_agent()


async def answer(message: str, deps: ChatDeps) -> ChatReply:
    result = await sales_agent.run(message, deps=deps)
    return result.output
