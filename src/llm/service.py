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
    def __init__(self, config: LLMConfig, llm=None):
        """Inicializa el servicio LLM con la configuración proporcionada."""
        self.llm = llm if llm is not None else OllamaLLM(
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

        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id=session_id)
            self._memories[session_id] = ConversationBufferMemory(return_messages=True)
        
        return self._sessions[session_id]

    async def _process_step(
            self,
            session_id: UUID,
            prompt_template,
            input_variables: Dict[str, Any],
            process_state: ProcessState,
            extract_markers: List[str],
            update_session_callback: Callable[[Session, Any], None],
            format_interaction: Callable[[Any], Tuple[str, str]],
            post_process_response: Callable[[Dict[str, str]], Any] = None
        ) -> Dict[str, Any]:
        """Procesa un paso del flujo de refinamiento."""
        try:
            session = self._get_session(session_id)
            session.state = process_state

            # Formatear el prompt y obtener la respuesta
            prompt = prompt_template.format(**input_variables)
            logger.debug(f"Prompt formateado: {prompt}")
            
            try:
                response = await self.llm.ainvoke(prompt)
                logger.debug(f"Respuesta del LLM: {response}")
            except Exception as e:
                logger.error(f"Error al invocar LLM: {str(e)}")
                raise
            
            # Extraer secciones si hay marcadores
            if extract_markers:
                extracted_sections = self._extract_sections(response, extract_markers)
                logger.debug(f"Secciones extraídas: {extracted_sections}")
                if post_process_response:
                    result = post_process_response(extracted_sections)
                    logger.debug(f"Resultado post-procesado: {result}")
                else:
                    result = {'text': response}
            else:
                result = {'text': response}
            
            # Actualizar la sesión con el resultado
            if update_session_callback:
                update_session_callback(session, result)
            
            # Formatear la interacción para la memoria
            if format_interaction:
                human_message, ai_message = format_interaction(result)
                await self._add_to_memory(session_id, human_message, ai_message)
            
            return result
            
        except Exception as e:
            logger.error(f"Error en _process_step: {str(e)}")
            raise

    async def refine_story(
        self,
        session_id: UUID,
        user_story: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refina una historia de usuario para mejorar su claridad y completitud."""
        try:
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
                    "Cambios Realizados:\n{}".format(
                        result['refined_story'],
                        result['refinement_feedback']
                    )
                )
                return human_message, ai_message

            def post_process_response(extracted_sections):
                refined_story = extracted_sections.get('**Historia Refinada:**', '').strip()
                refinement_feedback = extracted_sections.get('**Cambios Realizados:**', '').strip()
                return {
                    'refined_story': refined_story,
                    'refinement_feedback': refinement_feedback
                }

            result = await self._process_step(
                session_id=session_id,
                prompt_template=self.refinement_prompt,
                input_variables={
                    "user_story": user_story,
                    "feedback": feedback or "Sin feedback adicional.",
                },
                process_state=ProcessState.REFINEMENT,
                extract_markers=["**Historia Refinada:**", "**Cambios Realizados:**"],
                update_session_callback=update_session,
                format_interaction=format_interaction,
                post_process_response=post_process_response
            )

            return result
        except Exception as e:
            logger.error(f"Error en refine_story: {str(e)}")
            raise

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
                prompt_template=self.corner_case_prompt,
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
        """Propone estrategias de testing para una historia de usuario."""
        try:
            def update_session(session, result):
                session.testing_strategies = result['testing_strategies']
                session.testing_feedback = result['testing_feedback']

            def format_interaction(result):
                testing_strategies_formatted = '\n'.join(result['testing_strategies'])
                human_message = (
                    "Historia refinada:\n{}\n\n"
                    "Casos Esquina:\n{}\n\n"
                    "Estrategias de Testing Anteriores:\n{}\n\n"
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
                testing_strategies_text = extracted_sections.get('**Estrategias de Testing Actualizadas:**', '').strip()
                testing_strategies = [strategy.strip() for strategy in testing_strategies_text.split('\n') if strategy.strip()]
                testing_feedback = extracted_sections.get('**Análisis de Cambios:**', '').strip()
                return {
                    'testing_strategies': testing_strategies,
                    'testing_feedback': testing_feedback
                }

            result = await self._process_step(
                session_id=session_id,
                prompt_template=self.testing_strategy_prompt,
                input_variables={
                    "refined_user_story": refined_story,
                    "corner_cases": '\n'.join(corner_cases),
                    "existing_testing_strategies": '\n'.join(existing_testing_strategies) if existing_testing_strategies else "No hay estrategias de testing previas.",
                    "feedback": feedback or "Sin feedback adicional.",
                },
                process_state=ProcessState.TESTING_STRATEGY,
                extract_markers=["**Estrategias de Testing Actualizadas:**", "**Análisis de Cambios:**"],
                update_session_callback=update_session,
                format_interaction=format_interaction,
                post_process_response=post_process_response
            )

            return result
        except Exception as e:
            logger.error(f"Error en propose_testing_strategy: {str(e)}")
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
                logger.warning(f"Texto no es string: {type(text)}")
                return str(text)

            start_idx = text.find(start_marker)
            if start_idx == -1:
                logger.warning(f"No se encontró el marcador inicial: {start_marker}")
                return ""

            start_idx += len(start_marker)
            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    result = text[start_idx:].strip()
                    logger.debug(f"No se encontró el marcador final. Retornando: {result}")
                    return result
                result = text[start_idx:end_idx].strip()
                logger.debug(f"Sección extraída: {result}")
                return result
            result = text[start_idx:].strip()
            logger.debug(f"Sección extraída (sin marcador final): {result}")
            return result
        except Exception as e:
            logger.error(f"Error al extraer sección: {str(e)}")
            return ""

    async def _add_to_memory(self, session_id: UUID, human_message: str, ai_message: str):
        history = self._memories[session_id]
        history.chat_memory.add_user_message(human_message)
        history.chat_memory.add_ai_message(ai_message)

    async def close(self):
        """Cierra recursos y limpia el servicio LLM"""
        # Limpiar memorias
        self._memories.clear()
        # Cerrar cualquier otro recurso async si es necesario
        pass
