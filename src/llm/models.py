from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ProcessState(Enum):
    REFINEMENT = "refinement"
    CORNER_CASES = "corner_cases"
    TESTING_STRATEGY = "testing_strategy"

@dataclass
class Interaction:
    human_message: str
    ai_message: str
    process_state: ProcessState
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Session:
    session_id: UUID
    current_state: ProcessState = ProcessState.REFINEMENT
    interactions: List[Interaction] = field(default_factory=list)
    refined_story: Optional[str] = None
    corner_cases: List[str] = field(default_factory=list)
    corner_cases_feedback: Optional[str] = None
    testing_strategy: List[str] = field(default_factory=list)
    testing_strategy_feedback: Optional[str] = None

    def add_interaction(self, human_message: str, ai_message: str, process_state: ProcessState):
        """Añade una nueva interacción a la sesión."""
        self.interactions.append(
            Interaction(
                human_message=human_message,
                ai_message=ai_message,
                process_state=process_state
            )
        )