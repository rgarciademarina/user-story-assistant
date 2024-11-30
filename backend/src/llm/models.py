from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ProcessState(Enum):
    INITIAL = "initial"
    REFINEMENT = "refinement"
    CORNER_CASES = "corner_cases"
    TESTING_STRATEGY = "testing_strategy"
    FINALIZATION = "finalization"

@dataclass
class Interaction:
    human_message: str
    ai_message: str
    process_state: ProcessState
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Session:
    session_id: UUID
    state: ProcessState = ProcessState.REFINEMENT
    refined_story: Optional[str] = None
    refinement_feedback: Optional[str] = None
    corner_cases: Optional[List[str]] = None
    corner_cases_feedback: Optional[str] = None
    testing_strategy: Optional[List[str]] = None
    testing_strategy_feedback: Optional[str] = None
    finalized_story: Optional[str] = None
    finalization_feedback: Optional[str] = None
    interactions: List[Interaction] = field(default_factory=list)

    def add_interaction(self, human_message: str, ai_message: str, process_state: ProcessState):
        """Añade una nueva interacción a la sesión."""
        self.interactions.append(
            Interaction(
                human_message=human_message,
                ai_message=ai_message,
                process_state=process_state
            )
        )