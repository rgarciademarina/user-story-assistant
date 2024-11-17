from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class RefineStoryRequest(BaseModel):
    session_id: UUID
    story: str
    feedback: Optional[str] = None