import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app, override_llm_service

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_refine_story_endpoint(llm_service):
    """Test para el endpoint de refinamiento de historias de usuario con feedback"""
    # Configurar el servicio mock
    override_llm_service(llm_service)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api") as client:
        payload = {
            'story': 'Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal',
            'feedback': 'La historia debería especificar el método de autenticación y los datos a los que se accederá'
        }
        
        response = await client.post("/refine_story", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        
        response_json = response.json()
        assert "refined_story" in response_json, "Falta la clave 'refined_story' en la respuesta"
        assert "refinement_feedback" in response_json, "Falta la clave 'refinement_feedback' en la respuesta"
        
        refined_story = response_json["refined_story"]
        refinement_feedback = response_json["refinement_feedback"]

        assert isinstance(refined_story, str), "El valor de 'refined_story' debe ser una cadena"
        assert len(refined_story.strip()) > 0, "El valor de 'refined_story' no debe estar vacío"

        assert isinstance(refinement_feedback, str), "El valor de 'refinement_feedback' debe ser una cadena"
        assert len(refinement_feedback.strip()) > 0, "El valor de 'refinement_feedback' no debe estar vacío"
        
        # Verificar que el feedback se ha tenido en cuenta en la historia refinada
        assert any(["correo" in refined_story.lower() or 
                   "email" in refined_story.lower() or 
                   "contraseña" in refined_story.lower()]), \
            "La historia refinada debe incorporar el feedback sobre el método de autenticación"

        # Verificar que el feedback de refinamiento menciona los cambios realizados
        assert any(["método de autenticación" in refinement_feedback.lower() or
                    "datos" in refinement_feedback.lower()] ), \
            "El feedback de refinamiento debe mencionar los cambios realizados según el feedback proporcionado"