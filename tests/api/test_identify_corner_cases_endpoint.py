import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_identify_corner_cases_endpoint(llm_service):
    """Test para el endpoint de identificación de casos esquina con feedback"""
    refined_story = "Como usuario quiero..."
    payload = {
        'story': refined_story,
        'feedback': 'Considerar casos de autenticación de dos factores y bloqueos por inactividad'
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api") as client:
        response = await client.post("/identify_corner_cases", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"

        response_json = response.json()
        assert "corner_cases" in response_json, "Falta la clave 'corner_cases' en la respuesta"
        assert "corner_cases_feedback" in response_json, "Falta la clave 'corner_cases_feedback' en la respuesta"

        corner_cases = response_json["corner_cases"]
        corner_cases_feedback = response_json["corner_cases_feedback"]

        assert isinstance(corner_cases, list), "El valor de 'corner_cases' debe ser una lista"
        assert len(corner_cases) > 0, "La lista de 'corner_cases' no debe estar vacía"

        assert isinstance(corner_cases_feedback, str), "El valor de 'corner_cases_feedback' debe ser una cadena"
        assert len(corner_cases_feedback.strip()) > 0, "El valor de 'corner_cases_feedback' no debe estar vacío"

        # Verificar que el feedback se ha tenido en cuenta
        assert any(keyword in corner_cases_feedback.lower() for keyword in ["autenticación de dos factores", "inactividad"]), \
            "El feedback debe mencionar los cambios relacionados con el feedback proporcionado"