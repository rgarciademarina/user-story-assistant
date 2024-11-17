import logging
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from .config import LLMConfig, get_llm_config
from typing import List, Dict
from uuid import uuid4, UUID
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from .models import SessionState, ProcessState

# Importar las plantillas de prompts
from .prompts.refinement import refinement_prompt
from .prompts.corner_case import corner_case_prompt
from .prompts.testing import testing_strategy_prompt

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMService:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.sessions: Dict[UUID, SessionState] = {}
        self.memories: Dict[UUID, ConversationBufferWindowMemory] = {}
        
        self.llm = Ollama(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL,
            temperature=self.config.TEMPERATURE,
            max_length=self.config.MAX_LENGTH
        )
        
        # Inicializar las cadenas sin memoria (se añadirá en cada llamada)
        self.refinement_chain = LLMChain(
            llm=self.llm,
            prompt=refinement_prompt,
            verbose=True
        )
        self.corner_case_chain = LLMChain(
            llm=self.llm,
            prompt=corner_case_prompt,
            verbose=True
        )
        self.testing_strategy_chain = LLMChain(
            llm=self.llm,
            prompt=testing_strategy_prompt,
            verbose=True
        )

    def create_session(self) -> UUID:
        session_id = uuid4()
        self.sessions[session_id] = SessionState(
            session_id=session_id,
            current_state=ProcessState.REFINEMENT
        )
        self.memories[session_id] = ConversationBufferWindowMemory(
            k=5,
            return_messages=True,
            memory_key="chat_history",
            output_key="refined_story"
        )
        return session_id

    async def refine_story(self, session_id: UUID, user_story: str, feedback: str | None = None) -> str:
        memory = self.memories[session_id]
        session = self.sessions[session_id]
        
        try:
            refined_response = await self.refinement_chain.ainvoke(
                {
                    "user_story": user_story,
                    "feedback": feedback if feedback else "No hay feedback proporcionado.",
                    "chat_history": memory.chat_memory.messages
                },
                config={"memory": memory}
            )
            
            refined_story = self.extract_section(refined_response["text"], "**Historia Refinada:**")
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
            corner_case_response = await self.corner_case_chain.ainvoke(
                {
                    "refined_user_story": refined_story,
                    "feedback": feedback if feedback else "No hay feedback proporcionado.",
                    "chat_history": memory.chat_memory.messages
                },
                config={"memory": memory}
            )
            
            corner_cases_text = self.extract_section(corner_case_response["text"], "**Casos Esquina:**")
            # Convertir el texto en una lista de casos esquina
            corner_cases = [caso.strip() for caso in corner_cases_text.split('\n') if caso.strip()]
            
            session.corner_cases = corner_cases
            session.current_state = ProcessState.TESTING
            
            return corner_cases
        except Exception as e:
            logger.error(f"Error al identificar casos esquina: {e}")
            raise

    async def propose_testing_strategy(self, session_id: UUID, refined_story: str, corner_cases: List[str], feedback: str | None = None) -> List[str]:
        memory = self.memories[session_id]
        session = self.sessions[session_id]
        
        try:
            testing_strategy_response = await self.testing_strategy_chain.ainvoke(
                {
                    "refined_user_story": refined_story,
                    "corner_cases": "\n".join(corner_cases),
                    "feedback": feedback if feedback else "No hay feedback proporcionado.",
                    "chat_history": memory.chat_memory.messages
                },
                config={"memory": memory}
            )
            
            testing_strategies_text = self.extract_section(testing_strategy_response["text"], "**Estrategia de Testing:**", "**Fin de Estrategia**")
            testing_strategies = [strategy.strip() for strategy in testing_strategies_text.split('\n') if strategy.strip()]
            
            session.testing_strategies = testing_strategies
            session.current_state = ProcessState.COMPLETED
            
            return testing_strategies
        except Exception as e:
            logger.error(f"Error al proponer estrategias de testing: {e}")
            raise

    def extract_section(self, response: str, start_marker: str, end_marker: str = None) -> str:
        """
        Extrae una sección específica del texto entre los marcadores dados.
        """
        try:
            if not response or not isinstance(response, str):
                logger.error(f"Respuesta inválida: {response}")
                return ""
            
            start_idx = response.find(start_marker)
            if start_idx == -1:
                logger.error(f"No se encontró el marcador de inicio: {start_marker}")
                return ""
            
            start_idx += len(start_marker)
            
            if end_marker:
                end_idx = response.find(end_marker, start_idx)
                if end_idx == -1:
                    content = response[start_idx:].strip()
                else:
                    content = response[start_idx:end_idx].strip()
            else:
                content = response[start_idx:].strip()
            
            return content
        except Exception as e:
            logger.error(f"Error al extraer sección: {e}")
            return ""
