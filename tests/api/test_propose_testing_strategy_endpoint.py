import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
from src.main import app
from uuid import uuid4

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_propose_testing_strategy_endpoint(llm_service):
    """Test para el endpoint de propuesta de estrategias de testing con feedback"""
    refined_story = "Como usuario quiero..."
    corner_cases = [
        "1. Caso esquina 1",
        "2. Caso esquina 2"
    ]
    payload = {
        'story': refined_story,
        'corner_cases': corner_cases,
        'feedback': 'Incluir pruebas de estrés y seguridad avanzada'
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/propose_testing_strategy", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"

        response_json = response.json()
        assert "testing_strategies" in response_json, "Falta la clave 'testing_strategies' en la respuesta"
        assert "testing_feedback" in response_json, "Falta la clave 'testing_feedback' en la respuesta"

        testing_strategies = response_json["testing_strategies"]
        testing_feedback = response_json["testing_feedback"]

        assert isinstance(testing_strategies, list), "El valor de 'testing_strategies' debe ser una lista"
        assert len(testing_strategies) > 0, "La lista de 'testing_strategies' no debe estar vacía"

        assert isinstance(testing_feedback, str), "El valor de 'testing_feedback' debe ser una cadena"
        assert len(testing_feedback.strip()) > 0, "El valor de 'testing_feedback' no debe estar vacío"

        # Verificar que el feedback se ha tenido en cuenta
        assert any(keyword in testing_feedback.lower() for keyword in ["pruebas de estrés", "seguridad avanzada"]), \
            "El feedback debe mencionar los cambios relacionados con el feedback proporcionado"

@pytest.mark.asyncio
async def test_propose_testing_strategy_endpoint_with_existing_strategies(llm_service):
    """Test para el endpoint de propuesta de estrategias de testing con estrategias previas y feedback"""
    refined_story = "Como usuario quiero..."
    corner_cases = [
        "1. Caso esquina 1",
        "2. Caso esquina 2"
    ]
    existing_testing_strategies = [
        "1. Prueba inicial",
        "2. Prueba secundaria"
    ]
    payload = {
        'story': refined_story,
        'corner_cases': corner_cases,
        'feedback': 'Incluir pruebas de estrés y seguridad avanzada',
        'existing_testing_strategies': existing_testing_strategies
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/propose_testing_strategy", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"

        response_json = response.json()
        assert "testing_strategies" in response_json, "Falta la clave 'testing_strategies' en la respuesta"
        assert "testing_feedback" in response_json, "Falta la clave 'testing_feedback' en la respuesta"

        testing_strategies = response_json["testing_strategies"]
        testing_feedback = response_json["testing_feedback"]

        assert isinstance(testing_strategies, list), "El valor de 'testing_strategies' debe ser una lista"
        assert len(testing_strategies) > 0, "La lista de 'testing_strategies' no debe estar vacía"

        assert isinstance(testing_feedback, str), "El valor de 'testing_feedback' debe ser una cadena"
        assert len(testing_feedback.strip()) > 0, "El valor de 'testing_feedback' no debe estar vacío"

        # Verificar que el feedback se ha tenido en cuenta
        assert any(keyword in testing_feedback.lower() for keyword in ["pruebas de estrés", "seguridad avanzada"]), \
            "El feedback debe mencionar los cambios relacionados con el feedback proporcionado"