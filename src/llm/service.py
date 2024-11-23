import logging
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import HumanMessage, AIMessage, ChatMessage
from langchain.schema.runnable import RunnablePassthrough
from src.config.llm_config import LLMConfig
from langchain_ollama import OllamaLLM
from .models import Session, ProcessState
from langchain.chains import LLMChain
from typing import List, Dict, Any, Callable, Tuple, Optional
from uuid import uuid4, UUID

# Importar las plantillas de prompts
from .prompts.refinement import refinement_prompt
from .prompts.corner_case import corner_case_prompt
from .prompts.testing import testing_strategy_prompt

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config: LLMConfig):
        """Inicializa el servicio LLM con la configuración proporcionada."""
        self.llm = OllamaLLM(
            model=config.MODEL_NAME,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.TEMPERATURE
        )

        # Inicializar diccionarios de sesiones y memorias
        self._sessions: Dict[UUID, Session] = {}
        self._memories: Dict[UUID, ConversationBufferMemory] = {}
        
        # Usar los prompts importados directamente
        self.refinement_prompt = refinement_prompt
        self.corner_case_prompt = corner_case_prompt
        self.testing_strategy_prompt = testing_strategy_prompt

        # Crear los chains
        self.refinement_chain = LLMChain(
            llm=self.llm,
            prompt=self.refinement_prompt
        )
        
        self.corner_case_chain = LLMChain(
            llm=self.llm,
            prompt=self.corner_case_prompt
        )
        
        self.testing_strategy_chain = LLMChain(
            llm=self.llm,
            prompt=self.testing_strategy_prompt
        )

    def create_session(self) -> UUID:
        """Crea una nueva sesión y devuelve su ID."""
        session_id = uuid4()
        self._sessions[session_id] = Session(session_id=session_id)
        self._memories[session_id] = ConversationBufferMemory(return_messages=True)
        return session_id

    def _get_session(self, session_id: UUID) -> Session:
        """Obtiene una sesión existente o crea una nueva."""
        if not isinstance(session_id, UUID):
            try:
                session_id = UUID(str(session_id))
            except ValueError:
                raise ValueError(f"ID de sesión inválido: {session_id}")

        # Crear la sesión si no existe
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id=session_id)
            self._memories[session_id] = ConversationBufferMemory(return_messages=True)
        
        # Crear la memoria si no existe
        if session_id not in self._memories:
            self._memories[session_id] = ConversationBufferMemory(return_messages=True)
        
        return self._sessions[session_id]

    async def refine_story(
        self,
        session_id: UUID,
        user_story: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refina una historia de usuario para mejorar su claridad y completitud."""
        try:
            session = self._get_session(session_id)

            def update_session(session, result):
                session.refined_story = result['refined_story']
                session.refinement_feedback = result['refinement_feedback']

            def format_interaction(result):
                human_message = (
                    "Historia Original:\n{}\n\n"
                    "Feedback:\n{}".format(
                        user_story,
                        feedback or 'Sin feedback adicional.'
                    )
                )

                ai_message = (
                    "Historia Refinada:\n{}\n\n"
                    "Análisis de Cambios:\n{}".format(
                        result['refined_story'],
                        result['refinement_feedback']
                    )
                )

                return human_message, ai_message

            def post_process_response(extracted_sections):
                refined_story = extracted_sections.get('**Historia Refinada:**', '').strip()
                refinement_feedback = extracted_sections.get('**Análisis de Cambios:**', '').strip()
                return {
                    'refined_story': refined_story,
                    'refinement_feedback': refinement_feedback
                }

            result = await self._process_step(
                session_id=session_id,
                chain=self.refinement_chain,
                input_variables={
                    "user_story": user_story,
                    "feedback": feedback or "Sin feedback adicional.",
                },
                process_state=ProcessState.REFINEMENT,
                extract_markers=["**Historia Refinada:**", "**Análisis de Cambios:**"],
                update_session_callback=update_session,
                format_interaction=format_interaction,
                post_process_response=post_process_response
            )

            return result
        except Exception as e:
            logger.error(f"Error en refine_story: {str(e)}")
            raise

    async def _process_step(
        self,
        session_id: UUID,
        chain,
        input_variables: Dict[str, Any],
        process_state: ProcessState,
        extract_markers: List[str],
        update_session_callback: Callable[[Session, Any], None],
        format_interaction: Callable[[Any], Tuple[str, str]],
        post_process_response: Callable[[Dict[str, str]], Any] = None
    ) -> Any:
        """Procesa un paso del flujo de refinamiento."""
        try:
            session = self._get_session(session_id)
            session.current_state = process_state

            # Añadir el historial de conversación a las variables de entrada
            memory = self._memories[session_id]
            input_variables["chat_history"] = memory.buffer
            
            # Ejecutar el chain
            result = await chain.apredict(**input_variables)
            
            # Extraer secciones del resultado
            extracted_sections = self._extract_sections(result, extract_markers)
            
            # Post-procesar el resultado
            processed_result = post_process_response(extracted_sections)
            
            # Actualizar estado de la sesión
            update_session_callback(session, processed_result)
            
            # Formatear la interacción para el historial
            human_message, ai_message = format_interaction(processed_result)
            session.add_interaction(human_message, ai_message, process_state)

            # Actualizar la memoria de conversación
            memory.chat_memory.add_user_message(human_message)
            memory.chat_memory.add_ai_message(ai_message)
            
            return processed_result
        except Exception as e:
            logger.error(f"Error en _process_step: {str(e)}")
            raise

    def _extract_sections(self, text: str, markers: List[str]) -> Dict[str, str]:
        """Extrae secciones de texto basadas en marcadores."""
        sections = {}
        for i, marker in enumerate(markers):
            next_marker = markers[i + 1] if i + 1 < len(markers) else None
            section = self._extract_section(text, marker, next_marker)
            sections[marker] = section
        return sections

    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str] = None) -> str:
        """Extrae una sección de texto entre dos marcadores."""
        try:
            if not isinstance(text, str):
                return str(text)

            start_idx = text.find(start_marker)
            if start_idx == -1:
                return ""

            start_idx += len(start_marker)
            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    return text[start_idx:].strip()
                return text[start_idx:end_idx].strip()
            return text[start_idx:].strip()
        except Exception as e:
            logger.error(f"Error al extraer sección: {str(e)}")
            return ""

    async def identify_corner_cases(
        self,
        session_id: UUID,
        refined_story: str,
        feedback: Optional[str] = None,
        existing_corner_cases: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Identifica casos esquina en una historia de usuario refinada."""
        try:
            session = self._get_session(session_id)

            def update_session(session, result):
                session.corner_cases = result['corner_cases']
                session.corner_cases_feedback = result['corner_cases_feedback']

            def format_interaction(result):
                corner_cases_formatted = '\n'.join(result['corner_cases'])
                human_message = (
                    "Historia refinada:\n{}\n\n"
                    "Casos Esquina Anteriores:\n{}\n\n"
                    "Feedback:\n{}".format(
                        refined_story,
                        '\n'.join(existing_corner_cases) if existing_corner_cases else 'No hay casos esquina previos.',
                        feedback or 'Sin feedback adicional.'
                    )
                )

                ai_message = (
                    "Casos Esquina Actualizados:\n{}\n\n"
                    "Análisis de Cambios:\n{}".format(
                        corner_cases_formatted,
                        result['corner_cases_feedback']
                    )
                )

                return human_message, ai_message

            def post_process_response(extracted_sections):
                corner_cases_text = extracted_sections.get('**Casos Esquina Actualizados:**', '').strip()
                corner_cases = [case.strip() for case in corner_cases_text.split('\n') if case.strip()]
                corner_cases_feedback = extracted_sections.get('**Análisis de Cambios:**', '').strip()
                return {
                    'corner_cases': corner_cases,
                    'corner_cases_feedback': corner_cases_feedback
                }

            result = await self._process_step(
                session_id=session_id,
                chain=self.corner_case_chain,
                input_variables={
                    "refined_user_story": refined_story,
                    "existing_corner_cases": '\n'.join(existing_corner_cases) if existing_corner_cases else "No hay casos esquina previos.",
                    "feedback": feedback or "Sin feedback adicional.",
                },
                process_state=ProcessState.CORNER_CASES,
                extract_markers=["**Casos Esquina Actualizados:**", "**Análisis de Cambios:**"],
                update_session_callback=update_session,
                format_interaction=format_interaction,
                post_process_response=post_process_response
            )

            return result
        except Exception as e:
            logger.error(f"Error en identify_corner_cases: {str(e)}")
            raise

    async def propose_testing_strategy(
        self,
        session_id: UUID,
        refined_story: str,
        corner_cases: List[str],
        feedback: Optional[str] = None,
        existing_testing_strategies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        def update_session(session, result):
            session.testing_strategies = result['testing_strategies']
            session.testing_feedback = result['testing_feedback']

        def format_interaction(result):
            testing_strategies_formatted = '\n'.join(result['testing_strategies'])
            human_message = (
                "Historia refinada:\n{}\n\n"
                "Casos Esquina:\n{}\n\n"
                "Estrategias de Testing Anteriores:\n"
                "{}\n\n"
                "Feedback:\n{}".format(
                    refined_story,
                    '\n'.join(corner_cases),
                    '\n'.join(existing_testing_strategies) if existing_testing_strategies else 'No hay estrategias de testing previas.',
                    feedback or 'Sin feedback adicional.'
                )
            )

            ai_message = (
                "Estrategias de Testing Actualizadas:\n{}\n\n"
                "Análisis de Cambios:\n{}".format(
                    testing_strategies_formatted,
                    result['testing_feedback']
                )
            )

            return human_message, ai_message

        def post_process_response(extracted_sections):
            strategies_text = extracted_sections.get('**Estrategias de Testing Actualizadas:**', '').strip()
            testing_strategies = [strategy.strip() for strategy in strategies_text.split('\n') if strategy.strip()]
            testing_feedback = extracted_sections.get('**Análisis de Cambios:**', '').strip()
            return {
                'testing_strategies': testing_strategies,
                'testing_feedback': testing_feedback
            }

        input_vars = {
            "refined_user_story": refined_story,
            "corner_cases": '\n'.join(corner_cases),
            "existing_testing_strategies": '\n'.join(existing_testing_strategies) if existing_testing_strategies else "No hay estrategias de testing previas.",
            "feedback": feedback or "Sin feedback adicional.",
        }

        result = await self._process_step(
            session_id=session_id,
            chain=self.testing_strategy_chain,
            input_variables=input_vars,
            process_state=ProcessState.TESTING_STRATEGY,
            extract_markers=["**Estrategias de Testing Actualizadas:**", "**Análisis de Cambios:**"],
            update_session_callback=update_session,
            format_interaction=format_interaction,
            post_process_response=post_process_response
        )

        return result

    async def _add_to_memory(self, session_id: UUID, human_message: str, ai_message: str):
        history = self._memories[session_id]
        history.add_message(HumanMessage(content=human_message))
        history.add_message(AIMessage(content=ai_message))
