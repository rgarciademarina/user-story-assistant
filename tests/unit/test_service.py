import pytest
from src.llm.service import LLMService
from src.llm.config import LLMConfig

@pytest.fixture
def llm_config():
    """Fixture que proporciona una configuración de prueba para el LLM"""
    return LLMConfig(
        MODEL_NAME="llama3.2-vision",
        MODEL_TYPE="ollama",
        OLLAMA_BASE_URL="http://localhost:11434",
        MAX_LENGTH=2048,
        TEMPERATURE=0.7,
        API_HOST="0.0.0.0",
        API_PORT=8000,
        ENVIRONMENT="testing",
        LOG_LEVEL="DEBUG",
        DEBUG=True,
        VECTOR_STORE_PATH="./data/vector_store"
    )

@pytest.fixture
def llm_service(llm_config):
    """Fixture que proporciona una instancia del servicio LLM"""
    return LLMService(config=llm_config)

@pytest.mark.asyncio
async def test_refine_story(llm_service):
    user_story = """
    Como usuario quiero poder iniciar sesión 
    para acceder a mi cuenta personal
    """
    result = await llm_service.refine_story(user_story)

    # Verificar que se recibió una cadena refinada
    assert isinstance(result, str), "El resultado debe ser una cadena"
    assert len(result.strip()) > 0, "El resultado no debe estar vacío"

@pytest.mark.asyncio
async def test_identify_corner_cases(llm_service):
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."

    result = await llm_service.identify_corner_cases(refined_story)

    # Verificar que se recibe una lista de casos esquina
    assert isinstance(result, list), "El resultado debe ser una lista"
    assert len(result) > 0, "Debe haber al menos un caso esquina identificado"
    for caso in result:
        assert isinstance(caso, str), "Cada caso esquina debe ser una cadena"
        assert len(caso.strip()) > 0, "Los casos esquina no deben estar vacíos"

@pytest.mark.asyncio
async def test_propose_testing_strategy(llm_service):
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    corner_cases = ["1. **Nombre de Usuario/Correo electrónico no registrado:** El usuario intenta iniciar sesión con una dirección de correo electrónico o nombre de usuario que no se encuentra en la base de datos del sistema.", 
                    "2. **Contraseña Incorrecta persistente:** El usuario ingresa la contraseña incorrecta más de 10 veces consecutivas, lo que bloquea temporalmente su acceso al sistema.",
                    "3. **Problemas con autenticación de dos factores (2FA):** El usuario no puede iniciar sesión porque el sistema requiere la verificación del código de autenticación 2FA, pero el dispositivo del usuario no es compatible o no tiene el código disponible.",
                    "4. **Bloqueo de cuenta por seguridad:** La cuenta del usuario está bloqueada temporalmente debido a inactividad prolongada o actividad sospechosa, lo que impide su acceso hasta que se complete el proceso de desbloqueo.",
                    "5. **Compatibilidad con navegadores antiguos:** El sistema no es compatible con ciertos navegadores antiguos o versiones obsoletas, lo que limita la funcionalidad del inicio de sesión para algunos usuarios."]

    result = await llm_service.propose_testing_strategy(refined_story, corner_cases)

    # Verificar que se recibe una lista de estrategias de testing
    assert isinstance(result, list), "El resultado debe ser una lista"
    assert len(result) > 0, "Debe haber al menos una estrategia de testing propuesta"
    for estrategia in result:
        assert isinstance(estrategia, str), "Cada estrategia de testing debe ser una cadena"
        assert len(estrategia.strip()) > 0, "Las estrategias de testing no deben estar vacías"
