from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID

class ProcessState(Enum):
    REFINEMENT = "refinement"
    CORNER_CASES = "corner_cases"
    TESTING_STRATEGY = "testing_strategy"
    COMPLETED = "completed"

class SessionState(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    session_id: UUID
    current_state: ProcessState
    refined_story: str | None = None
    refinement_feedback: Optional[str] = None
    corner_cases: list[str] | None = None
    corner_cases_feedback: Optional[str] = None
    testing_strategies: Optional[list[str]] = None
    testing_feedback: Optional[str] = None