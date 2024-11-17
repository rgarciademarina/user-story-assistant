import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_identify_corner_cases_endpoint(llm_service):
    """Test para el endpoint de identificación de casos esquina con feedback"""
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    
    payload = {
        'story': refined_story,
        'feedback': 'Considerar también casos de autenticación de dos factores y bloqueos de cuenta por inactividad'
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
            if caso.strip():  # Solo validar líneas no vacías
                assert len(caso.strip()) > 0, "Los casos esquina no deben estar vacíos"
        
        # Verificar que el feedback se ha tenido en cuenta
        assert any(["2fa" in caso.lower() or 
                   "dos factores" in caso.lower() or 
                   "inactividad" in caso.lower() for caso in corner_cases if caso.strip()]), \
            "Los casos esquina deben incluir escenarios mencionados en el feedback"