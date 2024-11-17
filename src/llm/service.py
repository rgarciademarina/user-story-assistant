import logging
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from .config import LLMConfig, get_llm_config
from typing import List, Dict, Optional
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from .prompts.refinement import refinement_prompt
from .prompts.corner_case import corner_case_prompt
from .prompts.testing import testing_strategy_prompt

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMService:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = Ollama(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL,
            temperature=self.config.TEMPERATURE,
            max_length=self.config.MAX_LENGTH
        )
        
        # Diccionario para almacenar conversaciones por sesión
        self.conversations: Dict[str, ConversationChain] = {}
        
        # Construir las cadenas de procesamiento para cada prompt
        self.refinement_chain = refinement_prompt | self.llm
        self.corner_case_chain = corner_case_prompt | self.llm
        self.testing_strategy_chain = testing_strategy_prompt | self.llm

    def get_conversation_chain(self, session_id: str) -> ConversationChain:
        if session_id not in self.conversations:
            memory = ConversationBufferMemory(memory_key="history")
            self.conversations[session_id] = ConversationChain(
                llm=self.llm,
                memory=memory,
                verbose=True
            )
        return self.conversations[session_id]
    
    async def refine_story_with_context(self, user_story: str, session_id: str) -> str:
        """
        Refina una historia de usuario manteniendo el contexto de la conversación.
        
        Args:
            user_story: Historia de usuario en formato de texto.
            session_id: Identificador único de la sesión.
        
        Returns:
            str: Historia de usuario refinada.
        """
        try:
            # Utilizar la cadena de refinamiento específica con ainvoke
            response = await self.refinement_chain.ainvoke({"user_story": user_story})
            
            # Log de la respuesta completa del LLM
            logger.debug(f"Respuesta completa del LLM: {response}")
            
            refined_story = self.extract_section(response, "**Historia Refinada:**")
            logger.info(f"Historia Refinada: {refined_story}")
            
            return refined_story
        except Exception as e:
            logger.error(f"Error al refinar la historia con contexto: {e}")
            raise

    async def identify_corner_cases_with_context(self, refined_story: str, session_id: str) -> List[str]:
        """
        Identifica casos esquina en una historia de usuario refinada, manteniendo el contexto de la conversación.
        
        Args:
            refined_story: Historia de usuario refinada en formato de texto.
            session_id: Identificador único de la sesión.
        
        Returns:
            List[str]: Lista de casos esquina identificados.
        """
        try:
            # Opcional: puedes incluir el contexto adicional si es necesario
            corner_case_response = await self.corner_case_chain.ainvoke({"refined_user_story": refined_story})
            corner_cases = self.extract_section(corner_case_response, "**Casos Esquina:**")
            logger.info(f"Casos Esquina: {corner_cases}")
            return corner_cases.split('\n')  # Asumiendo que cada caso está en una nueva línea
        except Exception as e:
            logger.error(f"Error al identificar casos esquina con contexto: {e}")
            raise

    async def propose_testing_strategy_with_context(self, refined_story: str, corner_cases: List[str], session_id: str) -> List[str]:
        """
        Propone estrategias de testing basadas en la historia y casos identificados, manteniendo el contexto de la conversación.
        
        Args:
            refined_story: Historia de usuario refinada en formato de texto.
            corner_cases: Lista de casos esquina identificados.
            session_id: Identificador único de la sesión.
        
        Returns:
            List[str]: Lista de estrategias de testing propuestas.
        """
        try:
            # Puedes combinar corner_cases en una sola cadena si el prompt lo requiere
            corner_cases_str = "\n".join(corner_cases)
            testing_strategy_response = await self.testing_strategy_chain.ainvoke({
                "refined_user_story": refined_story,
                "corner_cases": corner_cases_str
            })
            testing_strategies = self.extract_section(testing_strategy_response, "**Estrategia de Testing:**", "**Fin de Estrategia**")
            logger.info(f"Estrategia de Testing: {testing_strategies}")
            return testing_strategies.split('\n')  # Asumiendo que cada estrategia está en una nueva línea
        except Exception as e:
            logger.error(f"Error al proponer estrategias de testing con contexto: {e}")
            raise

    def extract_section(self, response: str, start_marker: str, end_marker: Optional[str] = None) -> str:
        """
        Extrae una sección específica del texto entre los marcadores dados.
        
        Args:
            response (str): Texto completo de la respuesta.
            start_marker (str): Marcador de inicio de la sección.
            end_marker (str, optional): Marcador de fin de la sección. Defaults to None.
        
        Returns:
            str: Texto extraído de la sección.
        """
        try:
            start = response.find(start_marker)
            if start == -1:
                logger.warning(f"No se encontró el marcador de inicio: {start_marker}")
                return ""
            start += len(start_marker)
            if end_marker:
                end = response.find(end_marker, start)
                if end == -1:
                    end = len(response)
            else:
                end = len(response)
            extracted = response[start:end].strip()
            if not extracted:
                logger.warning("La sección extraída está vacía.")
            return extracted
        except Exception as e:
            logger.error(f"Error al extraer sección: {e}")
            return ""
