from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID

class ProcessState(str, Enum):
    REFINEMENT = "refinement"
    CORNER_CASES = "corner_cases"
    TESTING = "testing"
    COMPLETED = "completed"

class SessionState(BaseModel):
    session_id: UUID
    current_state: ProcessState
    refined_story: Optional[str] = None
    corner_cases: Optional[list[str]] = None
    testing_strategies: Optional[list[str]] = None