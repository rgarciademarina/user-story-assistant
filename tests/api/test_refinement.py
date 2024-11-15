import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
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

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_refine_story_endpoint(llm_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        sample_story = {
            'story': 'Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal'
        }
        response = await client.post("/refine_story", json=sample_story)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        response_json = response.json()
        assert "refined_story" in response_json, "Falta la clave 'refined_story' en la respuesta"
        refined_story = response_json["refined_story"]
        assert isinstance(refined_story, str), "El valor de 'refined_story' debe ser una cadena"
        assert len(refined_story.strip()) > 0, "El valor de 'refined_story' no debe estar vacío"

@pytest.mark.asyncio
async def test_identify_corner_cases_endpoint(llm_service):
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    
    payload = {
        'story': refined_story
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/identify_corner_cases", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        response_json = response.json()
        assert "corner_cases" in response_json, "Falta la clave 'corner_cases' en la respuesta"
        corner_cases = response_json["corner_cases"]
        assert isinstance(corner_cases, list), "El valor de 'corner_cases' debe ser una lista"
        assert len(corner_cases) > 0, "La lista de 'corner_cases' no debe estar vacía"
        for caso in corner_cases:
            assert isinstance(caso, str), "Cada caso esquina debe ser una cadena"
            assert len(caso.strip()) > 0, "Los casos esquina no deben estar vacíos"

@pytest.mark.asyncio
async def test_propose_testing_strategy_endpoint(llm_service):
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    corner_cases = [
        "1. **Nombre de Usuario/Correo electrónico no registrado:** El usuario intenta iniciar sesión con una dirección de correo electrónico o nombre de usuario que no se encuentra en la base de datos del sistema.",
        "2. **Contraseña Incorrecta persistente:** El usuario ingresa la contraseña incorrecta más de 10 veces consecutivas, lo que bloquea temporalmente su acceso al sistema.",
        "3. **Problemas con autenticación de dos factores (2FA):** El usuario no puede iniciar sesión porque el sistema requiere la verificación del código de autenticación 2FA, pero el dispositivo del usuario no es compatible o no tiene el código disponible.",
        "4. **Bloqueo de cuenta por seguridad:** La cuenta del usuario está bloqueada temporalmente debido a inactividad prolongada o actividad sospechosa, lo que impide su acceso hasta que se complete el proceso de desbloqueo.",
        "5. **Compatibilidad con navegadores antiguos:** El sistema no es compatible con ciertos navegadores antiguos o versiones obsoletas, lo que limita la funcionalidad del inicio de sesión para algunos usuarios."
    ]
    
    payload = {
        'story': refined_story,
        'corner_cases': corner_cases
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/propose_testing_strategy", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        response_json = response.json()
        assert "testing_strategies" in response_json, "Falta la clave 'testing_strategies' en la respuesta"
        testing_strategies = response_json["testing_strategies"]
        assert isinstance(testing_strategies, list), "El valor de 'testing_strategies' debe ser una lista"
        assert len(testing_strategies) > 0, "La lista de 'testing_strategies' no debe estar vacía"
        for estrategia in testing_strategies:
            assert isinstance(estrategia, str), "Cada estrategia de testing debe ser una cadena"
