from pydantic import BaseModel, Field, field_validator
import html

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="Raw emotional prompt text input from user")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        # Strip whitespace
        val = v.strip()
        if not val:
            raise ValueError("Prompt cannot be empty or only whitespace")
        if len(val) > 500:
            raise ValueError("Prompt must be 500 characters or less")
        # Sanitize HTML tags
        val = html.escape(val)
        return val

class PromptResponse(BaseModel):
    request_id: str
    prompt: str
    emotion_type: str
    confidence: float
