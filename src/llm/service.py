import json
import logging
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from .config import LLMConfig, get_llm_config
from typing import List

# Importar las plantillas de prompts
from .prompts.refinement import refinement_prompt
from .prompts.corner_case import corner_case_prompt
from .prompts.testing import testing_strategy_prompt

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMService:
    def __init__(self, config: LLMConfig = None):
        self.config = config or get_llm_config()
        self.llm = Ollama(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL,
            temperature=self.config.TEMPERATURE
        )
        
        # Construir las cadenas de procesamiento para cada prompt
        self.refinement_chain = refinement_prompt | self.llm
        self.corner_case_chain = corner_case_prompt | self.llm
        self.testing_strategy_chain = testing_strategy_prompt | self.llm

    async def analyze_user_story(self, user_story: str) -> dict:
        """
        Analiza una historia de usuario y proporciona recomendaciones.
        
        Args:
            user_story: El texto de la historia de usuario a analizar.
            
        Returns:
            dict: Diccionario con mejoras, casos esquina y estrategias de testing.
        """
        try:
            # Refinar la historia de usuario
            refined_response = await self.refinement_chain.ainvoke({"user_story": user_story})
            logger.debug(f"Respuesta Refinamiento: {refined_response}")
            refined_story = self.extract_section(refined_response, "**Historia Refinada:**")
            logger.info(f"Historia Refinada: {refined_story}")
            
            # Identificar casos esquina
            corner_case_response = await self.corner_case_chain.ainvoke({"refined_user_story": refined_story})
            logger.debug(f"Respuesta Casos Esquina: {corner_case_response}")
            corner_cases = self.extract_section(corner_case_response, "**Casos Esquina:**")
            logger.info(f"Casos Esquina: {corner_cases}")
            
            # Sugerir estrategia de testing
            testing_strategy_response = await self.testing_strategy_chain.ainvoke({
                "refined_user_story": refined_story,
                "corner_cases": corner_cases
            })
            logger.debug(f"Respuesta Estrategia Testing: {testing_strategy_response}")
            testing_strategy = self.extract_section(testing_strategy_response, "**Estrategia de Testing:**", "**Fin de Estrategia**")
            logger.info(f"Estrategia de Testing: {testing_strategy}")
            
            return {
                "improvements": refined_story,
                "edge_cases": corner_cases,
                "testing_strategies": testing_strategy
            }
        except Exception as e:
            logger.error(f"Error al analizar la historia de usuario: {str(e)}")
            raise Exception(f"Error al analizar la historia de usuario: {str(e)}")

    def extract_section(self, text: str, start_marker: str, end_marker: str = None) -> str:
        """
        Extrae una sección específica del texto entre dos marcadores.
        
        Args:
            text: El texto completo del que extraer.
            start_marker: Marca de inicio de la sección.
            end_marker: Marca de fin de la sección. Si es None, extrae hasta el final del texto.
        
        Returns:
            str: El contenido extraído entre los marcadores.
        """
        try:
            start = text.index(start_marker) + len(start_marker)
            if end_marker:
                end = text.index(end_marker, start)
                return text[start:end].strip()
            else:
                return text[start:].strip()
        except ValueError:
            logger.warning(f"No se pudo encontrar los marcadores {start_marker} y {end_marker} en el texto.")
            return ""

    async def refine_story(self, user_story: str) -> str:
        """
        Refina una historia de usuario.

        Args:
            user_story: Historia de usuario en formato de texto.

        Returns:
            str: Historia de usuario refinada.
        """
        try:
            refined_response = await self.refinement_chain.ainvoke({"user_story": user_story})
            refined_story = self.extract_section(refined_response, "**Historia Refinada:**")
            logger.info(f"Historia Refinada: {refined_story}")
            return refined_story
        except Exception as e:
            logger.error(f"Error al refinar la historia: {e}")
            raise

    async def identify_corner_cases(self, refined_story: str) -> List[str]:
        """
        Identifica casos esquina en una historia de usuario refinada.

        Args:
            refined_story: Historia de usuario refinada en formato de texto.

        Returns:
            List[str]: Lista de casos esquina identificados.
        """
        try:
            corner_case_response = await self.corner_case_chain.ainvoke({"refined_user_story": refined_story})
            corner_cases = self.extract_section(corner_case_response, "**Casos Esquina:**")
            logger.info(f"Casos Esquina: {corner_cases}")
            return corner_cases.split('\n')  # Asumiendo que cada caso está en una nueva línea
        except Exception as e:
            logger.error(f"Error al identificar casos esquina: {e}")
            raise

    async def propose_testing_strategy(self, refined_story: str, corner_cases: List[str]) -> List[str]:
        """
        Propone estrategias de testing basadas en la historia y casos identificado.

        Args:
            refined_story: Historia de usuario refinada en formato de texto.
            corner_cases: Lista de casos esquina identificados.

        Returns:
            List[str]: Lista de estrategias de testing propuestas.
        """
        try:
            testing_strategy_response = await self.testing_strategy_chain.ainvoke({
                "refined_user_story": refined_story,
                "corner_cases": corner_cases
            })
            testing_strategies = self.extract_section(testing_strategy_response, "**Estrategia de Testing:**", "**Fin de Estrategia**")
            logger.info(f"Estrategia de Testing: {testing_strategies}")
            return testing_strategies.split('\n')  # Asumiendo que cada estrategia está en una nueva línea
        except Exception as e:
            logger.error(f"Error al proponer estrategias de testing: {e}")
            raise
