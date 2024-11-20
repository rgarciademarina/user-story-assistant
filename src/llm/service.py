import logging
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from src.config.llm_config import LLMConfig
from typing import List, Dict, Any, Callable, Tuple
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

    async def _process_step(
        self,
        session_id: UUID,
        chain,
        input_variables: Dict[str, Any],
        process_state: ProcessState,
        extract_markers: List[str],
        update_session_callback: Callable[[SessionState, Any], None],
        format_interaction: Callable[[Any], Tuple[str, str]],
        post_process_response: Callable[[Dict[str, str]], Any] = None
    ) -> Any:
        memory = self.memories[session_id]
        session = self.sessions[session_id]
        session.current_state = process_state

        try:
            # Añadir el input original del usuario a la memoria
            if "feedback" in input_variables:
                original_input = f"Input del usuario:\n{input_variables.get('user_story', '')}\nFeedback: {input_variables.get('feedback', 'No hay feedback')}"
            else:
                original_input = f"Input del usuario:\n{input_variables.get('user_story', input_variables.get('refined_user_story', ''))}"
            
            memory.add_message(HumanMessage(content=original_input))
            
            input_variables["chat_history"] = memory.messages
            if "feedback" in input_variables and not input_variables["feedback"]:
                input_variables["feedback"] = "No hay feedback proporcionado."

            response = await chain.ainvoke(input_variables)
            extracted_sections = self.extract_multiple_sections(response, extract_markers)

            if post_process_response:
                result = post_process_response(extracted_sections)
            else:
                result = extracted_sections

            update_session_callback(session, result)

            human_message, ai_message = format_interaction(result)
            
            # Añadir la interacción formateada a la memoria
            memory.add_message(HumanMessage(content=human_message))
            memory.add_message(AIMessage(content=ai_message))

            return result
        except Exception as e:
            logger.error(f"Error en el paso {process_state.name}: {e}")
            raise

    def extract_multiple_sections(self, text: str, markers: List[str]) -> Dict[str, str]:
        sections = {}
        for i, marker in enumerate(markers):
            start_index = text.find(marker)
            if start_index != -1:
                start_index += len(marker)
                end_index = text.find(markers[i+1], start_index) if i+1 < len(markers) else len(text)
                sections[marker] = text[start_index:end_index].strip()
            else:
                sections[marker] = ''
        return sections

    async def refine_story(self, session_id: UUID, user_story: str, feedback: str | None = None) -> Dict[str, str]:
        def update_session(session, result):
            session.refined_story = result['refined_story']
            session.refinement_feedback = result['refinement_feedback']

        def format_interaction(result):
            human_message = f"Historia original: {user_story}\nFeedback: {feedback}"
            ai_message = f"Historia refinada: {result['refined_story']}\nCambios realizados: {result['refinement_feedback']}"
            return human_message, ai_message

        def post_process_response(extracted_sections):
            return {
                'refined_story': extracted_sections.get('**Historia Refinada:**', '').strip(),
                'refinement_feedback': extracted_sections.get('**Cambios Realizados:**', '').strip()
            }

        input_vars = {
            "user_story": user_story,
            "feedback": feedback,
        }

        result = await self._process_step(
            session_id=session_id,
            chain=self.refinement_chain,
            input_variables=input_vars,
            process_state=ProcessState.REFINEMENT,
            extract_markers=["**Historia Refinada:**", "**Cambios Realizados:**"],
            update_session_callback=update_session,
            format_interaction=format_interaction,
            post_process_response=post_process_response
        )

        return result

    async def identify_corner_cases(self, session_id: UUID, refined_story: str, feedback: str | None = None) -> Dict[str, Any]:
        def update_session(session, result):
            session.corner_cases = result['corner_cases']
            session.corner_cases_feedback = result['corner_cases_feedback']

        def format_interaction(result):
            corner_cases_formatted = '\n'.join(result['corner_cases'])
            human_message = f"Historia refinada: {refined_story}\nFeedback: {feedback}"
            ai_message = f"Casos esquina identificados:\n{corner_cases_formatted}\nAnálisis de Cambios:\n{result['corner_cases_feedback']}"
            return human_message, ai_message

        def post_process_response(extracted_sections):
            corner_cases_text = extracted_sections.get('**Casos Esquina:**', '').strip()
            corner_cases = [case.strip() for case in corner_cases_text.split('\n') if case.strip()]
            corner_cases_feedback = extracted_sections.get('**Análisis de Cambios:**', '').strip()
            return {
                'corner_cases': corner_cases,
                'corner_cases_feedback': corner_cases_feedback
            }

        input_vars = {
            "refined_user_story": refined_story,
            "feedback": feedback,
        }

        result = await self._process_step(
            session_id=session_id,
            chain=self.corner_case_chain,
            input_variables=input_vars,
            process_state=ProcessState.CORNER_CASES,
            extract_markers=["**Casos Esquina:**", "**Análisis de Cambios:**"],
            update_session_callback=update_session,
            format_interaction=format_interaction,
            post_process_response=post_process_response
        )

        return result

    async def propose_testing_strategy(self, session_id: UUID, refined_story: str, corner_cases: List[str], feedback: str | None = None) -> Dict[str, Any]:
        def update_session(session, result):
            session.testing_strategies = result['testing_strategies']
            session.testing_feedback = result['testing_feedback']

        def format_interaction(result):
            testing_strategies_formatted = '\n'.join(result['testing_strategies'])
            human_message = f"Historia refinada: {refined_story}\nCasos esquina: {corner_cases}\nFeedback: {feedback}"
            ai_message = f"Estrategias de Testing propuestas:\n{testing_strategies_formatted}\nAnálisis de Cambios:\n{result['testing_feedback']}"
            return human_message, ai_message

        def post_process_response(extracted_sections):
            testing_strategies_text = extracted_sections.get('**Estrategias de Testing:**', '').strip()
            testing_strategies = [strategy.strip() for strategy in testing_strategies_text.split('\n') if strategy.strip()]
            testing_feedback = extracted_sections.get('**Análisis de Cambios:**', '').strip()
            return {
                'testing_strategies': testing_strategies,
                'testing_feedback': testing_feedback
            }

        input_vars = {
            "refined_user_story": refined_story,
            "corner_cases": '\n'.join(corner_cases),
            "feedback": feedback,
        }

        result = await self._process_step(
            session_id=session_id,
            chain=self.testing_strategy_chain,
            input_variables=input_vars,
            process_state=ProcessState.TESTING_STRATEGY,
            extract_markers=["**Estrategias de Testing:**", "**Análisis de Cambios:**"],
            update_session_callback=update_session,
            format_interaction=format_interaction,
            post_process_response=post_process_response
        )

        return result

    async def _add_to_memory(self, session_id: UUID, human_message: str, ai_message: str):
        history = self.memories[session_id]
        history.add_message(HumanMessage(content=human_message))
        history.add_message(AIMessage(content=ai_message))
