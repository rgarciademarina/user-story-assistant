import logging
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from src.config.llm_config import LLMConfig
from typing import List, Dict
from uuid import uuid4, UUID
from langchain_ollama import OllamaLLM
from .models import SessionState, ProcessState
from langchain.chains import LLMChain

# Importar las plantillas de prompts
from .prompts.refinement import refinement_prompt
from .prompts.corner_case import corner_case_prompt
from .prompts.testing import testing_strategy_prompt

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMService:
    def __init__(self, config: LLMConfig):
        # Crear el modelo LLM basado en la configuración
        self.llm = OllamaLLM(
            model=config.MODEL_NAME,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.TEMPERATURE
        )
        self.sessions: Dict[UUID, SessionState] = {}
        self.memories: Dict[UUID, ChatMessageHistory] = {}
        
        # Usar los prompts importados directamente
        self.refinement_prompt = refinement_prompt
        self.corner_case_prompt = corner_case_prompt
        self.testing_strategy_prompt = testing_strategy_prompt
        
        # Crear secuencias ejecutables
        self.refinement_chain = (
            RunnablePassthrough() | 
            self.refinement_prompt | 
            self.llm
        )
        
        self.corner_case_chain = (
            RunnablePassthrough() | 
            self.corner_case_prompt | 
            self.llm
        )
        
        self.testing_strategy_chain = (
            RunnablePassthrough() | 
            self.testing_strategy_prompt | 
            self.llm
        )

    def create_session(self) -> UUID:
        session_id = uuid4()
        self.sessions[session_id] = SessionState(
            session_id=session_id,
            current_state=ProcessState.REFINEMENT
        )
        self.memories[session_id] = ChatMessageHistory()
        return session_id

    def extract_section(self, text: str, start_marker: str) -> str:
        try:
            if not isinstance(text, str):
                return str(text)
                
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return text
            
            content_start = start_idx + len(start_marker)
            return text[content_start:].strip()
        except Exception as e:
            logger.error(f"Error al extraer sección: {e}")
            return str(text)

    async def refine_story(self, session_id: UUID, user_story: str, feedback: str | None = None) -> str:
        memory = self.memories[session_id]
        session = self.sessions[session_id]
        
        try:
            response = await self.refinement_chain.ainvoke({
                "user_story": user_story,
                "feedback": feedback if feedback else "No hay feedback proporcionado.",
                "chat_history": memory.messages
            })
            
            refined_story = self.extract_section(response, "**Historia Refinada:**")
            session.refined_story = refined_story
            session.current_state = ProcessState.CORNER_CASES
            
            return refined_story
        except Exception as e:
            logger.error(f"Error al refinar la historia: {e}")
            raise

    async def identify_corner_cases(self, session_id: UUID, refined_story: str, feedback: str | None = None) -> List[str]:
        memory = self.memories[session_id]
        session = self.sessions[session_id]
        
        try:
            response = await self.corner_case_chain.ainvoke({
                "refined_user_story": refined_story,
                "feedback": feedback if feedback else "No hay feedback proporcionado.",
                "chat_history": memory.messages
            })
            
            corner_cases_text = self.extract_section(response, "**Casos Esquina:**")
            corner_cases = [caso.strip() for caso in corner_cases_text.split('\n') if caso.strip()]
            
            session.corner_cases = corner_cases
            session.current_state = ProcessState.TESTING_STRATEGY
            
            return corner_cases
        except Exception as e:
            logger.error(f"Error al identificar casos esquina: {e}")
            raise

    async def propose_testing_strategy(self, session_id: UUID, refined_story: str, corner_cases: List[str], feedback: str | None = None) -> List[str]:
        memory = self.memories[session_id]
        session = self.sessions[session_id]
        
        try:
            response = await self.testing_strategy_chain.ainvoke({
                "refined_user_story": refined_story,
                "corner_cases": "\n".join(corner_cases),
                "feedback": feedback if feedback else "No hay feedback proporcionado.",
                "chat_history": memory.messages
            })
            
            strategies_text = self.extract_section(response, "**Estrategias de Testing:**")
            strategies = [strategy.strip() for strategy in strategies_text.split('\n') if strategy.strip()]
            
            session.current_state = ProcessState.COMPLETED
            
            return strategies
        except Exception as e:
            logger.error(f"Error al proponer estrategias de testing: {e}")
            raise

    async def _add_to_memory(self, session_id: UUID, human_message: str, ai_message: str):
        history = self.memories[session_id]
        history.add_message(HumanMessage(content=human_message))
        history.add_message(AIMessage(content=ai_message))
