from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    model: str | None = None
    think: bool = False


class ChatResponse(BaseModel):
    model: str
    response: str
    total_duration_ns: int | None = None
    eval_count: int | None = None
    eval_duration_ns: int | None = None
