import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_refine_story_endpoint(llm_service):
    """Test para el endpoint de refinamiento de historias de usuario con feedback"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            'story': 'Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal',
            'feedback': 'La historia debería especificar el método de autenticación y los datos a los que se accederá'
        }
        
        response = await client.post("/refine_story", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        
        response_json = response.json()
        assert "refined_story" in response_json, "Falta la clave 'refined_story' en la respuesta"
        
        refined_story = response_json["refined_story"]
        assert isinstance(refined_story, str), "El valor de 'refined_story' debe ser una cadena"
        assert len(refined_story.strip()) > 0, "El valor de 'refined_story' no debe estar vacío"
        
        # Verificar que el feedback se ha tenido en cuenta
        assert any(["correo" in refined_story.lower() or 
                   "email" in refined_story.lower() or 
                   "contraseña" in refined_story.lower()]), \
            "La historia refinada debe incorporar el feedback sobre el método de autenticación"