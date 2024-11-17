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
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = Ollama(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL,
            temperature=self.config.TEMPERATURE,
            max_length=self.config.MAX_LENGTH
        )
        
        # Construir las cadenas de procesamiento para cada prompt
        self.refinement_chain = refinement_prompt | self.llm
        self.corner_case_chain = corner_case_prompt | self.llm
        self.testing_strategy_chain = testing_strategy_prompt | self.llm

    async def refine_story(self, user_story: str, feedback: str | None = None) -> str:
        """
        Refina una historia de usuario.
    
        Args:
            user_story: Historia de usuario en formato de texto.
            feedback: Feedback opcional del usuario sobre la historia refinada anterior.
    
        Returns:
            str: Historia de usuario refinada.
        """
        try:
            refined_response = await self.refinement_chain.ainvoke({
                "user_story": user_story,
                "feedback": feedback if feedback else "No hay feedback proporcionado."
            })
            
            refined_story = self.extract_section(refined_response, "**Historia Refinada:**")
            logger.info(f"Historia Refinada: {refined_story}")
            return refined_story
        except Exception as e:
            logger.error(f"Error al refinar la historia: {e}")
            raise

    async def identify_corner_cases(self, refined_story: str, feedback: str | None = None) -> List[str]:
        """
        Identifica casos esquina en una historia de usuario refinada.
    
        Args:
            refined_story: Historia de usuario refinada en formato de texto.
            feedback: Feedback opcional del usuario sobre los casos esquina identificados anteriormente.
    
        Returns:
            List[str]: Lista de casos esquina identificados.
        """
        try:
            corner_case_response = await self.corner_case_chain.ainvoke({
                "refined_user_story": refined_story,
                "feedback": feedback if feedback else "No hay feedback proporcionado."
            })
            corner_cases = self.extract_section(corner_case_response, "**Casos Esquina:**")
            logger.info(f"Casos Esquina: {corner_cases}")
            return corner_cases.split('\n')  # Asumiendo que cada caso está en una nueva línea
        except Exception as e:
            logger.error(f"Error al identificar casos esquina: {e}")
            raise

    async def propose_testing_strategy(self, refined_story: str, corner_cases: List[str], feedback: str | None = None) -> List[str]:
        """
        Propone estrategias de testing basadas en la historia y casos identificados.
    
        Args:
            refined_story: Historia de usuario refinada en formato de texto.
            corner_cases: Lista de casos esquina identificados.
            feedback: Feedback opcional del usuario sobre las estrategias de testing propuestas anteriormente.
    
        Returns:
            List[str]: Lista de estrategias de testing propuestas.
        """
        try:
            testing_strategy_response = await self.testing_strategy_chain.ainvoke({
                "refined_user_story": refined_story,
                "corner_cases": "\n".join(corner_cases),
                "feedback": feedback if feedback else "No hay feedback proporcionado."
            })
            testing_strategies = self.extract_section(testing_strategy_response, "**Estrategia de Testing:**", "**Fin de Estrategia**")
            logger.info(f"Estrategia de Testing: {testing_strategies}")
            return testing_strategies.split('\n')
        except Exception as e:
            logger.error(f"Error al proponer estrategias de testing: {e}")
            raise

    def extract_section(self, response: str, start_marker: str, end_marker: str = None) -> str:
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
                return ""
            start += len(start_marker)
            if end_marker:
                end = response.find(end_marker, start)
                if end == -1:
                    end = len(response)
            else:
                end = len(response)
            return response[start:end].strip()
        except Exception as e:
            logger.error(f"Error al extraer sección: {e}")
            return ""
