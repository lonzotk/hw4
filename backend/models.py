from pydantic import BaseModel, Field
from dataclasses import dataclass, field


class ProductCard(BaseModel):
    product_id: str
    name: str
    price: float
    description: str
    image_url: str
    sizes_in_stock: list[str] = Field(default_factory=list)


class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductLookup(BaseModel):
    product_id: str
    product_name: str
    description: str | None = None
    price: float | None = None
    sizes: list[SizeStock] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_token: str | None = None
    page_context: str | None = Field(default=None, max_length=500)


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    created_at: str


@dataclass
class ChatDeps:
    customer_name: str | None = None
    customer_email: str | None = None
    page_context: str | None = None
    history: list[ChatHistoryItem] = field(default_factory=list)


class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
